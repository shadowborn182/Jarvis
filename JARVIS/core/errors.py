"""
JARVIS — Global Error Handler (Prefix + Slash + Database + API Timeouts)
Developer: Shadow
"""

from __future__ import annotations

import asyncio
import logging
import traceback
from typing import Any

import discord
from discord import app_commands
from discord.ext import commands
from sqlalchemy.exc import SQLAlchemyError

from core.branding import error_embed, warning_embed
from core.checks import BotOwnerOnly, GuildOwnerOnly, ModRoleRequired

logger = logging.getLogger("JARVIS.Errors")


def _format_missing_perms(perms: list[str]) -> str:
    return ", ".join(f"`{p.replace('_', ' ').title()}`" for p in perms)


async def handle_prefix_command_error(ctx: commands.Context, error: commands.CommandError) -> None:
    """Centralized error handler for all prefix commands."""
    # Unwrap CommandInvokeError
    original: Any = getattr(error, "original", error)

    if isinstance(error, commands.CommandNotFound):
        return

    if isinstance(error, commands.DisabledCommand):
        await ctx.reply(
            embed=warning_embed("Command Disabled", "This command is currently disabled."),
            mention_author=False,
        )
        return

    if isinstance(error, commands.NoPrivateMessage):
        await ctx.reply(
            embed=warning_embed("Server Only", "This command can only be used inside a Discord server."),
            mention_author=False,
        )
        return

    if isinstance(error, (BotOwnerOnly, GuildOwnerOnly, ModRoleRequired)):
        await ctx.reply(
            embed=error_embed("Access Denied", str(error)),
            mention_author=False,
        )
        return

    if isinstance(error, commands.MissingPermissions):
        await ctx.reply(
            embed=error_embed(
                "Missing Permissions",
                f"You need {_format_missing_perms(error.missing_permissions)} to use this command.",
            ),
            mention_author=False,
        )
        return

    if isinstance(error, commands.BotMissingPermissions):
        await ctx.reply(
            embed=error_embed(
                "JARVIS Missing Permissions",
                f"JARVIS needs {_format_missing_perms(error.missing_permissions)} to complete this action.",
            ),
            mention_author=False,
        )
        return

    if isinstance(error, commands.CommandOnCooldown):
        await ctx.reply(
            embed=warning_embed(
                "Cooldown Active",
                f"Please wait `{error.retry_after:.1f}s` before using this command again.",
            ),
            mention_author=False,
        )
        return

    if isinstance(error, (commands.MissingRequiredArgument, commands.BadArgument, commands.BadUnionArgument)):
        prefix = ctx.clean_prefix
        usage = f"`{prefix}{ctx.command.qualified_name} {ctx.command.signature}`".strip()
        await ctx.reply(
            embed=warning_embed(
                "Invalid Arguments",
                f"{error}\n\n**Usage:** {usage}",
            ),
            mention_author=False,
        )
        return

    if isinstance(original, SQLAlchemyError):
        logger.exception("Database error in command %s: %s", ctx.command, original)
        await ctx.reply(
            embed=error_embed(
                "Database Error",
                "JARVIS encountered a temporary database issue. Please try again shortly.",
            ),
            mention_author=False,
        )
        return

    if isinstance(original, (asyncio.TimeoutError, discord.HTTPException)):
        if isinstance(original, discord.HTTPException) and original.status == 429:
            logger.warning("Discord rate limit hit during command %s", ctx.command)
            await ctx.reply(
                embed=warning_embed("Rate Limited", "Discord is rate-limiting requests. Try again in a moment."),
                mention_author=False,
            )
            return
        logger.warning("Discord/Network error in command %s: %s", ctx.command, original)
        await ctx.reply(
            embed=error_embed("Network Timeout", "A network or Discord API timeout occurred. Please retry."),
            mention_author=False,
        )
        return

    # Unexpected internal error
    tb = "".join(traceback.format_exception(type(original), original, original.__traceback__))
    logger.error("Unhandled prefix command error (%s):\n%s", ctx.command, tb)
    await ctx.reply(
        embed=error_embed(
            "Unexpected Error",
            "An internal error occurred while executing this command. It has been logged for review.",
        ),
        mention_author=False,
    )


async def handle_app_command_error(
    interaction: discord.Interaction,
    error: app_commands.AppCommandError,
) -> None:
    """Centralized error handler for all slash/app commands."""
    original: Any = getattr(error, "original", error)

    async def send_safe(embed: discord.Embed) -> None:
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed, ephemeral=True)
        else:
            await interaction.response.send_message(embed=embed, ephemeral=True)

    if isinstance(error, app_commands.MissingPermissions):
        await send_safe(
            error_embed(
                "Missing Permissions",
                f"You need {_format_missing_perms(error.missing_permissions)} to use this command.",
            )
        )
        return

    if isinstance(error, app_commands.BotMissingPermissions):
        await send_safe(
            error_embed(
                "JARVIS Missing Permissions",
                f"JARVIS needs {_format_missing_perms(error.missing_permissions)} to run this command.",
            )
        )
        return

    if isinstance(error, app_commands.CommandOnCooldown):
        await send_safe(
            warning_embed(
                "Cooldown Active",
                f"Please wait `{error.retry_after:.1f}s` before trying again.",
            )
        )
        return

    if isinstance(error, app_commands.CheckFailure):
        await send_safe(error_embed("Access Denied", str(error)))
        return

    if isinstance(original, SQLAlchemyError):
        logger.exception("Database error in slash command %s: %s", interaction.command, original)
        await send_safe(
            error_embed("Database Error", "A temporary database issue occurred. Please retry.")
        )
        return

    logger.exception("Unhandled app command error (%s): %s", interaction.command, original)
    await send_safe(
        error_embed(
            "Unexpected Error",
            "An unexpected error occurred while processing this slash command.",
        )
    )
