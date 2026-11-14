"""
JARVIS — Reusable Prefix & Slash Command Checks
Developer: Shadow
"""

from __future__ import annotations

from typing import Callable, TypeVar

import discord
from discord import app_commands
from discord.ext import commands

T = TypeVar("T")


class BotOwnerOnly(commands.CheckFailure):
    """Raised when a non-owner attempts to run a JARVIS developer command."""


class GuildOwnerOnly(commands.CheckFailure):
    """Raised when a non-server-owner attempts to run a server-owner-only command."""


class ModRoleRequired(commands.CheckFailure):
    """Raised when a user lacks moderator permissions or configured mod roles."""


class PremiumRequired(commands.CheckFailure):
    """Raised when a command or feature requires an active server Premium subscription."""


def is_jarvis_owner() -> Callable[[T], T]:
    """Check whether the invoking user is configured in BOT_OWNER_IDS."""

    async def predicate(ctx: commands.Context) -> bool:
        owner_ids = getattr(ctx.bot, "owner_ids", set())
        if ctx.author.id in owner_ids or await ctx.bot.is_owner(ctx.author):
            return True
        raise BotOwnerOnly("This command is restricted to JARVIS developer/owners.")

    return commands.check(predicate)


def is_guild_owner_only() -> Callable[[T], T]:
    """Check whether the invoking user owns the current Discord server."""

    async def predicate(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        if ctx.author.id == ctx.guild.owner_id:
            return True
        raise GuildOwnerOnly("Only the server owner can execute this command.")

    return commands.check(predicate)


def is_guild_premium() -> Callable[[T], T]:
    """Check whether the current Discord server has an active JARVIS Premium subscription."""

    async def predicate(ctx: commands.Context) -> bool:
        if ctx.guild is None:
            raise commands.NoPrivateMessage()
        premium_svc = getattr(ctx.bot, "premium", None)
        if premium_svc is None:
            raise PremiumRequired("Premium service is currently unavailable.")
        status = await premium_svc.get_guild_status(ctx.guild.id)
        if not status.is_premium:
            raise PremiumRequired(
                "This feature requires **JARVIS Premium** for this server. "
                "Run `premium info` to inspect Premium plans or ask the bot owner (**Shadow**) to activate."
            )
        return True

    return commands.check(predicate)


def app_is_guild_owner_only():
    """Slash command equivalent checking server ownership."""

    async def predicate(interaction: discord.Interaction) -> bool:
        if interaction.guild is None:
            raise app_commands.NoPrivateMessage()
        if interaction.user.id == interaction.guild.owner_id:
            return True
        raise app_commands.CheckFailure("Only the server owner can execute this command.")

    return app_commands.check(predicate)
