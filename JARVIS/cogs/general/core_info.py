"""
JARVIS — Phase 1 Core Commands (Prefix + Slash Hybrid)
Commands: ping, botinfo, uptime, prefix, modules, health, sync
Developer: Shadow
"""

from __future__ import annotations

import platform
import time
from datetime import datetime, timezone

import discord
import psutil
from discord import app_commands
from discord.ext import commands

from config import BOT_DESCRIPTION, BOT_NAME, BOT_VERSION, DEVELOPER_NAME, OFFICIAL_CATEGORIES
from core.branding import (
    JarvisColors,
    JarvisEmojis,
    error_embed,
    jarvis_embed,
    success_embed,
)
from core.checks import is_jarvis_owner
from core.utilities import format_duration


def require_perms_doc(label: str):
    """Attach permission metadata for dynamic display in the JARVIS help menu."""
    def decorator(func):
        func.__jarvis_perms__ = label
        return func
    return decorator


class CoreInfoCog(commands.Cog):
    """Essential JARVIS diagnostics, branding, prefix management, and module status."""

    category = "General"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="ping",
        description="Check JARVIS WebSocket gateway and database latency.",
    )
    async def ping(self, ctx: commands.Context) -> None:
        ws_ms = round(self.bot.latency * 1000, 1)
        start = time.perf_counter()
        db_ok = await self.bot.db.health_check() if hasattr(self.bot, "db") else False
        db_ms = round((time.perf_counter() - start) * 1000, 1)

        embed = jarvis_embed(
            title=f"{JarvisEmojis.BRAND} {BOT_NAME} Latency",
            color=JarvisColors.SUCCESS if db_ok else JarvisColors.WARNING,
        )
        embed.add_field(name="Gateway Latency", value=f"`{ws_ms} ms`", inline=True)
        embed.add_field(
            name="Database Latency",
            value=f"`{db_ms} ms` ({'Healthy' if db_ok else 'Unavailable'})",
            inline=True,
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="uptime",
        description="Show how long JARVIS has been running without interruption.",
    )
    async def uptime(self, ctx: commands.Context) -> None:
        started_at: datetime = getattr(self.bot, "started_at", datetime.now(timezone.utc))
        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        embed = jarvis_embed(
            title=f"{JarvisEmojis.BRAND} {BOT_NAME} Uptime",
            description=f"Online for **{format_duration(elapsed)}**\nStarted: <t:{int(started_at.timestamp())}:F>",
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="botinfo",
        aliases=["about", "jarvis"],
        description="Display JARVIS identity, developer credit, runtime metrics, and server statistics.",
    )
    async def botinfo(self, ctx: commands.Context) -> None:
        started_at: datetime = getattr(self.bot, "started_at", datetime.now(timezone.utc))
        elapsed = (datetime.now(timezone.utc) - started_at).total_seconds()
        process = psutil.Process()
        mem_mb = process.memory_info().rss / (1024 * 1024)
        total_members = sum(g.member_count or 0 for g in self.bot.guilds)

        embed = jarvis_embed(
            title=f"{JarvisEmojis.BRAND} {BOT_NAME} — System Information",
            description=BOT_DESCRIPTION,
            color=JarvisColors.BRAND,
        )
        embed.add_field(name="Developer", value=f"**{DEVELOPER_NAME}**", inline=True)
        embed.add_field(name="Version", value=f"`v{BOT_VERSION}`", inline=True)
        embed.add_field(name="Python / discord.py", value=f"`{platform.python_version()}` / `{discord.__version__}`", inline=True)
        embed.add_field(name="Servers", value=f"`{len(self.bot.guilds):,}`", inline=True)
        embed.add_field(name="Total Members", value=f"`{total_members:,}`", inline=True)
        embed.add_field(name="Loaded Commands", value=f"`{len(self.bot.commands)}`", inline=True)
        embed.add_field(name="Memory Usage", value=f"`{mem_mb:.1f} MB`", inline=True)
        embed.add_field(name="Uptime", value=f"`{format_duration(elapsed)}`", inline=True)
        embed.add_field(name="Gateway Ping", value=f"`{round(self.bot.latency * 1000, 1)} ms`", inline=True)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="prefix",
        description="View or update the server prefix for JARVIS prefix commands.",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @require_perms_doc("Manage Server")
    @app_commands.describe(new_prefix="New prefix (1–10 characters). Leave empty to view current prefix.")
    async def prefix(self, ctx: commands.Context, new_prefix: str | None = None) -> None:
        assert ctx.guild is not None
        if new_prefix is None:
            current = await self.bot.get_server_prefix(ctx.guild.id)
            await ctx.reply(
                embed=jarvis_embed(
                    title=f"{JarvisEmojis.PREFIX} Server Prefix",
                    description=f"Current JARVIS prefix for **{ctx.guild.name}**: `{current}`",
                ),
                mention_author=False,
            )
            return

        cleaned = new_prefix.strip()
        if not cleaned or len(cleaned) > 10:
            await ctx.reply(
                embed=error_embed("Invalid Prefix", "Prefix must be between 1 and 10 characters with no spaces."),
                mention_author=False,
            )
            return
        if " " in cleaned:
            await ctx.reply(
                embed=error_embed("Invalid Prefix", "Prefix cannot contain whitespace."),
                mention_author=False,
            )
            return

        await self.bot.db.set_guild_prefix(ctx.guild.id, cleaned)
        await self.bot.prefix_cache.set(ctx.guild.id, cleaned)
        await ctx.reply(
            embed=success_embed(
                "Prefix Updated",
                f"JARVIS prefix for **{ctx.guild.name}** is now `{cleaned}`.",
            ),
            mention_author=False,
        )

    @commands.hybrid_command(
        name="modules",
        description="List all 17 JARVIS modules and currently loaded Cog extensions.",
    )
    async def modules(self, ctx: commands.Context) -> None:
        loaded_exts = list(self.bot.extensions.keys())
        embed = jarvis_embed(
            title=f"{JarvisEmojis.BRAND} {BOT_NAME} Architecture Modules",
            description=f"`{len(loaded_exts)}` Python Cog extension(s) currently active.",
        )
        cat_lines = [
            f"{JarvisEmojis.CATEGORY_MAP.get(cat, '•')} **{cat}**"
            for cat in OFFICIAL_CATEGORIES
        ]
        embed.add_field(name="17 Official Modules", value="\n".join(cat_lines), inline=True)
        embed.add_field(
            name="Active Extensions",
            value="\n".join(f"`{ext}`" for ext in loaded_exts) or "None",
            inline=True,
        )
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command(
        name="sync",
        description="Sync JARVIS slash commands to Discord (Bot Owner only).",
        hidden=True,
    )
    @is_jarvis_owner()
    @require_perms_doc("Bot Owner")
    async def sync_commands(self, ctx: commands.Context, scope: str = "global") -> None:
        if scope == "guild" and ctx.guild is not None:
            self.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await self.bot.tree.sync(guild=ctx.guild)
        else:
            synced = await self.bot.tree.sync()
        await ctx.reply(
            embed=success_embed(
                "Slash Commands Synced",
                f"Successfully synced `{len(synced)}` application command(s) ({scope}).",
            ),
            mention_author=False,
        )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(CoreInfoCog(bot))
