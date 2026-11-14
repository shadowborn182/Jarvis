"""
JARVIS — No Prefix Command Engine (Premium Feature with Anti-Spam & False-Positive Protection)
Developer: Shadow
"""

from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from sqlalchemy import select

from core.cache import AsyncTTLCache
from database.models import GuildBranding, GuildSettings

if TYPE_CHECKING:
    from bot import JarvisBot


# Anti-spam: max 5 No Prefix invocations per 10 seconds per user in a guild
NO_PREFIX_MAX_CALLS = 5
NO_PREFIX_WINDOW_SECONDS = 10.0

# Commands that accept zero positional arguments; trailing prose like "ping me later" must NOT trigger them
ZERO_ARG_COMMANDS = frozenset({"ping", "uptime", "botinfo", "about", "jarvis", "modules", "serverinfo"})


class NoPrefixService:
    """Evaluates whether a message qualifies as a valid Premium No-Prefix command invocation."""

    def __init__(self, bot: JarvisBot) -> None:
        self.bot = bot
        self._enabled_cache: AsyncTTLCache[int, bool] = AsyncTTLCache(ttl_seconds=120.0)
        self._rate_buckets: dict[tuple[int, int], deque[float]] = defaultdict(deque)

    async def invalidate(self, guild_id: int) -> None:
        await self._enabled_cache.invalidate(guild_id)

    async def is_enabled_for_guild(self, guild_id: int) -> bool:
        """Return True only if both GuildBranding.no_prefix_enabled AND active guild Premium are True."""
        status = await self.bot.premium.get_guild_status(guild_id)
        if not status.is_premium:
            return False

        cached = await self._enabled_cache.get(guild_id)
        if cached is not None:
            return cached

        async with self.bot.db.session_factory() as session:
            res = await session.execute(
                select(GuildBranding.no_prefix_enabled).where(GuildBranding.guild_id == guild_id)
            )
            enabled = bool(res.scalar_one_or_none() or False)

        await self._enabled_cache.set(guild_id, enabled)
        return enabled

    async def set_enabled_for_guild(self, guild_id: int, enabled: bool) -> None:
        await self.bot.db.update_guild_branding(guild_id, no_prefix_enabled=enabled)
        await self._enabled_cache.set(guild_id, enabled)

    def _check_rate_limit(self, guild_id: int, user_id: int) -> bool:
        """Sliding window anti-spam protection for No Prefix calls."""
        now = time.monotonic()
        key = (guild_id, user_id)
        bucket = self._rate_buckets[key]
        while bucket and (now - bucket[0]) > NO_PREFIX_WINDOW_SECONDS:
            bucket.popleft()
        if len(bucket) >= NO_PREFIX_MAX_CALLS:
            return False
        bucket.append(now)
        return True

    def _lookup_command(self, token: str) -> commands.Command | None:
        """Look up a registered top-level command or alias (case-insensitive)."""
        return self.bot.all_commands.get(token.lower())

    async def _is_ignored(self, guild_id: int, channel_id: int, user_id: int, cmd_name: str) -> bool:
        async with self.bot.db.session_factory() as session:
            res = await session.execute(
                select(
                    GuildSettings.ignored_channel_ids,
                    GuildSettings.ignored_user_ids,
                    GuildSettings.ignored_commands,
                ).where(GuildSettings.guild_id == guild_id)
            )
            row = res.first()
            if row is None:
                return False
            ignored_channels, ignored_users, ignored_cmds = row
            if channel_id in (ignored_channels or []):
                return True
            if user_id in (ignored_users or []):
                return True
            if cmd_name.lower() in {c.lower() for c in (ignored_cmds or [])}:
                return True
            return False

    def looks_like_command(self, content: str, cmd: commands.Command) -> bool:
        """
        Prevent normal conversation from accidentally triggering No Prefix commands:
        - Reject multi-line prose.
        - Reject zero-arg commands if extra trailing words exist (e.g. 'ping me tomorrow').
        - For 'help', reject long natural-language sentences (e.g. 'help me fix my pc please').
        """
        stripped = content.strip()
        if not stripped or "\n" in stripped:
            return False

        # Ignore messages starting with common conversational punctuation
        if stripped[0] in ('"', "'", ".", ",", "!", "?", "(", "[", "<", "*", "~", "`"):
            return False

        parts = stripped.split()
        if not parts:
            return False

        root_name = cmd.qualified_name.lower()

        if root_name in ZERO_ARG_COMMANDS and len(parts) > 1:
            return False

        if root_name == "help":
            # Allow 'help', 'help ping', 'help General', 'h general' — reject casual sentences > 3 words
            if len(parts) > 3:
                return False
            if len(parts) >= 2 and parts[1].lower() in {"me", "us", "please", "pls", "bro", "man", "anyone"}:
                return False

        if root_name in {"avatar", "av", "userinfo", "ui", "whois"} and len(parts) > 4:
            return False

        return True

    async def should_trigger_no_prefix(self, message: discord.Message) -> bool:
        """Full validation pipeline deciding if `""` should be accepted as a prefix for this message."""
        if message.guild is None or message.author.bot or message.webhook_id is not None:
            return False

        content = message.content.strip()
        if not content:
            return False

        first_token = content.split(maxsplit=1)[0]
        # Must be alphanumeric/underscore command name (no prefix symbols)
        if not first_token.replace("_", "").isalnum():
            return False

        cmd = self._lookup_command(first_token)
        if cmd is None or cmd.hidden or not cmd.enabled:
            return False

        if not self.looks_like_command(content, cmd):
            return False

        if not await self.is_enabled_for_guild(message.guild.id):
            return False

        if await self._is_ignored(message.guild.id, message.channel.id, message.author.id, cmd.qualified_name):
            return False

        if not self._check_rate_limit(message.guild.id, message.author.id):
            return False

        return True
