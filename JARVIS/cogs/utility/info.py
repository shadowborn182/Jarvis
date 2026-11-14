"""
JARVIS — Utility Information Commands (avatar, serverinfo, userinfo)
All work with Prefix, No-Prefix (Premium), and Slash commands and apply server branding.
Developer: Shadow
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands


class UtilityInfoCog(commands.Cog):
    """Essential server and user lookup commands."""

    category = "Utility"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_command(
        name="avatar",
        aliases=["av", "pfp"],
        description="Display a member's full-resolution avatar.",
    )
    @app_commands.describe(member="Target user (defaults to yourself)")
    async def avatar(self, ctx: commands.Context, member: discord.Member | discord.User | None = None) -> None:
        target = member or ctx.author
        guild_id = ctx.guild.id if ctx.guild else None
        embed = await self.bot.make_embed(
            guild_id,
            title=f"Avatar — {target.display_name}",
            description=f"[Open Original Avatar]({target.display_avatar.url})",
        )
        embed.set_image(url=target.display_avatar.with_size(1024).url)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="serverinfo",
        aliases=["si", "guildinfo"],
        description="Display detailed statistics and configuration for this server.",
    )
    @commands.guild_only()
    async def serverinfo(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        guild = ctx.guild
        status = await self.bot.premium.get_guild_status(guild.id)

        embed = await self.bot.make_embed(
            guild.id,
            title=f"Server Information — {guild.name}",
            description=guild.description or "No server description set.",
        )
        if guild.icon and not embed.thumbnail.url:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="Server ID", value=f"`{guild.id}`", inline=True)
        embed.add_field(name="Owner", value=f"{guild.owner.mention if guild.owner else 'Unknown'}", inline=True)
        embed.add_field(name="Members", value=f"`{guild.member_count or len(guild.members):,}`", inline=True)
        embed.add_field(name="Text / Voice", value=f"`{len(guild.text_channels)}` / `{len(guild.voice_channels)}`", inline=True)
        embed.add_field(name="Roles", value=f"`{len(guild.roles)}`", inline=True)
        embed.add_field(
            name="JARVIS Premium",
            value=f"`{status.plan_name}`" if status.is_premium else "`Free Tier`",
            inline=True,
        )
        embed.add_field(name="Created", value=f"<t:{int(guild.created_at.timestamp())}:R>", inline=True)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.hybrid_command(
        name="userinfo",
        aliases=["ui", "whois"],
        description="Display profile details, join date, and roles for a user.",
    )
    @app_commands.describe(member="Target member (defaults to yourself)")
    async def userinfo(self, ctx: commands.Context, member: discord.Member | None = None) -> None:
        target = member or ctx.author
        guild_id = ctx.guild.id if ctx.guild else None
        embed = await self.bot.make_embed(
            guild_id,
            title=f"User Information — {target.display_name}",
        )
        if not embed.thumbnail.url:
            embed.set_thumbnail(url=target.display_avatar.url)
        embed.add_field(name="Username", value=f"`{target}`", inline=True)
        embed.add_field(name="User ID", value=f"`{target.id}`", inline=True)
        embed.add_field(name="Account Created", value=f"<t:{int(target.created_at.timestamp())}:R>", inline=True)

        if isinstance(target, discord.Member):
            if target.joined_at:
                embed.add_field(name="Joined Server", value=f"<t:{int(target.joined_at.timestamp())}:R>", inline=True)
            roles = [r.mention for r in reversed(target.roles) if not r.is_default()]
            roles_txt = ", ".join(roles[:10]) + (f" (+{len(roles) - 10})" if len(roles) > 10 else "")
            embed.add_field(name=f"Roles ({len(roles)})", value=roles_txt or "None", inline=False)

        await ctx.reply(embed=embed, mention_author=False)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(UtilityInfoCog(bot))
