"""
JARVIS — Core Lifecycle Events (Guild Provisioning, Reconnection & Error Recovery)
Developer: Shadow
"""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

logger = logging.getLogger("JARVIS.Events")


class CoreEvents(commands.Cog):
    """Handles core Discord gateway and guild lifecycle events."""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self) -> None:
        user = self.bot.user
        logger.info(
            "JARVIS online as %s (ID: %s) | Servers: %d | Shards: %s",
            user,
            user.id if user else "N/A",
            len(self.bot.guilds),
            self.bot.shard_count or 1,
        )

    @commands.Cog.listener()
    async def on_resumed(self) -> None:
        logger.info("JARVIS gateway session resumed.")

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        logger.info("Joined guild %s (%s) with %s members.", guild.name, guild.id, guild.member_count)
        db = getattr(self.bot, "db", None)
        if db is not None:
            await db.ensure_guild(guild.id)

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        logger.info("Removed from guild %s (%s).", guild.name, guild.id)
        prefix_cache = getattr(self.bot, "prefix_cache", None)
        if prefix_cache is not None:
            await prefix_cache.invalidate(guild.id)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CoreEvents(bot))
