"""
JARVIS — Main Bot Entrypoint
Advanced All-In-One Discord Management Bot
Developer: Shadow
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
from datetime import datetime, timezone
from itertools import cycle

import discord
from discord.ext import commands, tasks

from cogs.general.help import JarvisHelpView
from config import (
    BOT_DESCRIPTION,
    BOT_NAME,
    DEVELOPER_NAME,
    Settings,
    get_settings,
    validate_bot_startup_env,
)
from core.branding import JarvisColors, jarvis_embed
from core.cache import AsyncTTLCache
from core.database import DatabaseManager
from core.errors import handle_app_command_error, handle_prefix_command_error
from core.loader import load_all_extensions
from core.logger import setup_logging
from core.noprefix import NoPrefixService
from core.premium import PremiumService


async def resolve_prefix(bot: JarvisBot, message: discord.Message) -> list[str]:
    """
    Dynamic per-guild prefix resolver:
    1. Supports standard mention + persisted per-server prefix.
    2. When guild has active Premium + No Prefix enabled and message passes safety guards,
       includes '' so valid registered commands execute without a prefix.
    """
    if message.guild is None:
        return commands.when_mentioned_or(bot.settings.default_prefix)(bot, message)

    prefix = await bot.get_server_prefix(message.guild.id)
    prefixes = commands.when_mentioned_or(prefix)(bot, message)

    if await bot.noprefix.should_trigger_no_prefix(message):
        prefixes.append("")

    return prefixes


class JarvisBot(commands.AutoShardedBot):
    """JARVIS AutoShardedBot orchestrating modular Cogs, Premium, No-Prefix, async DB, and presence."""

    def __init__(self, settings: Settings) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        intents.moderation = True
        intents.guilds = True
        intents.voice_states = True

        super().__init__(
            command_prefix=resolve_prefix,
            intents=intents,
            help_command=None,  # Replaced by custom interactive JarvisHelpView
            case_insensitive=True,
            strip_after_prefix=True,
            owner_ids=settings.owner_ids or None,
            description=BOT_DESCRIPTION,
        )

        self.settings: Settings = settings
        self.db: DatabaseManager = DatabaseManager(settings)
        self.premium: PremiumService = PremiumService(self.db)
        self.noprefix: NoPrefixService = NoPrefixService(self)
        self.prefix_cache: AsyncTTLCache[int, str] = AsyncTTLCache(ttl_seconds=300.0)
        self.started_at: datetime = datetime.now(timezone.utc)
        self._presence_templates = cycle(
            [
                "JARVIS | /help",
                "Protecting {servers} Servers",
                f"Developed by {DEVELOPER_NAME}",
            ]
        )
        self.logger = logging.getLogger(BOT_NAME)

    async def get_server_prefix(self, guild_id: int) -> str:
        cached = await self.prefix_cache.get(guild_id)
        if cached is not None:
            return cached
        prefix = await self.db.get_guild_prefix(guild_id)
        await self.prefix_cache.set(guild_id, prefix)
        return prefix

    async def make_embed(
        self,
        guild_id: int | None,
        *,
        title: str | None = None,
        description: str | None = None,
        color: int = JarvisColors.BRAND,
        footer_note: str | None = None,
    ) -> discord.Embed:
        """Build a JARVIS embed automatically applying Premium server branding when active."""
        if guild_id is None:
            return jarvis_embed(title=title, description=description, color=color, footer_note=footer_note)
        status = await self.premium.get_guild_status(guild_id)
        if not status.is_premium:
            return jarvis_embed(title=title, description=description, color=color, footer_note=footer_note)
        branding = await self.db.get_guild_branding(guild_id)
        return jarvis_embed(
            title=title,
            description=description,
            color=color,
            footer_note=footer_note,
            branding=branding,
            is_premium=True,
        )

    async def setup_hook(self) -> None:
        """Initialize database, core events, all Cogs, persistent views, and presence loop."""
        self.logger.info("Initializing %s by %s...", BOT_NAME, DEVELOPER_NAME)

        await self.db.init_models()
        await self.load_extension("core.events")

        report = await load_all_extensions(self)
        self.logger.info(
            "Extensions loaded: %d | Failed: %d | Skipped: %d",
            len(report.loaded),
            len(report.failed),
            len(report.skipped),
        )

        self.tree.on_error = handle_app_command_error
        self.add_view(JarvisHelpView(self, prefix=self.settings.default_prefix, timeout=None))

        if not self.rotate_presence.is_running():
            self.rotate_presence.start()

    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        await handle_prefix_command_error(ctx, error)

    @tasks.loop(seconds=30)
    async def rotate_presence(self) -> None:
        template = next(self._presence_templates)
        text = template.format(servers=len(self.guilds))
        activity = discord.Activity(type=discord.ActivityType.watching, name=text)
        await self.change_presence(status=discord.Status.online, activity=activity)

    @rotate_presence.before_loop
    async def before_rotate_presence(self) -> None:
        await self.wait_until_ready()

    async def close(self) -> None:
        self.logger.info("Shutting down %s gracefully...", BOT_NAME)
        if self.rotate_presence.is_running():
            self.rotate_presence.cancel()
        await super().close()
        await self.db.close()


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level)
    validate_bot_startup_env(settings)

    bot = JarvisBot(settings)

    loop = asyncio.get_running_loop()
    for sig_name in ("SIGINT", "SIGTERM"):
        sig = getattr(signal, sig_name, None)
        if sig is not None:
            try:
                loop.add_signal_handler(sig, lambda: asyncio.create_task(bot.close()))
            except NotImplementedError:
                pass

    async with bot:
        await bot.start(settings.discord_token)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
