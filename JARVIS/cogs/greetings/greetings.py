"""
JARVIS — Custom Welcome & Goodbye Banners, Embeds & Event Listeners
Developer: Shadow
"""

from __future__ import annotations

import logging

import discord
from discord.ext import commands

from core.banners import render_welcome_goodbye_banner
from core.branding import apply_guild_branding, jarvis_embed, success_embed

logger = logging.getLogger("JARVIS.Greetings")


def _render_variables(template: str, member: discord.Member) -> str:
    guild = member.guild
    return (
        template.replace("{user}", member.display_name)
        .replace("{username}", str(member))
        .replace("{mention}", member.mention)
        .replace("{server}", guild.name)
        .replace("{member_count}", str(guild.member_count or len(guild.members)))
    )


def _command_meta(perms: str = "Manage Server"):
    def decorator(func):
        func.__jarvis_perms__ = perms
        func.__jarvis_noprefix__ = True
        return func
    return decorator


class GreetingsCog(commands.Cog):
    """Welcome & Goodbye channel automation with Premium Pillow banners."""

    category = "Greetings"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def _dispatch_greeting(
        self,
        member: discord.Member,
        *,
        kind: str,
        target_channel: discord.TextChannel,
    ) -> None:
        guild = member.guild
        welcome_cfg = await self.bot.db.get_welcome_settings(guild.id)
        branding = await self.bot.db.get_guild_branding(guild.id)
        status = await self.bot.premium.get_guild_status(guild.id)

        if kind == "welcome":
            raw_msg = welcome_cfg.welcome_message or "Welcome to **{server}**, {mention}! You are member #{member_count}."
            banner_enabled = branding.welcome_banner_enabled if status.is_premium else True
            bg_url = branding.welcome_banner_bg_url if status.is_premium else None
            custom_text = branding.welcome_banner_text if status.is_premium else None
            text_color = branding.welcome_banner_text_color if status.is_premium else "#F8FAFC"
            accent_color = branding.welcome_banner_accent_color if status.is_premium else "#38BDF8"
            text_pos = branding.welcome_banner_text_position if status.is_premium else "center"
            title = f"Welcome, {member.display_name}"
        else:
            raw_msg = welcome_cfg.goodbye_message or "**{user}** has left **{server}**. We now have {member_count} members."
            banner_enabled = branding.goodbye_banner_enabled if status.is_premium else True
            bg_url = branding.goodbye_banner_bg_url if status.is_premium else None
            custom_text = branding.goodbye_banner_text if status.is_premium else None
            text_color = branding.goodbye_banner_text_color if status.is_premium else "#F8FAFC"
            accent_color = branding.goodbye_banner_accent_color if status.is_premium else "#F59E0B"
            text_pos = branding.goodbye_banner_text_position if status.is_premium else "center"
            title = f"Goodbye, {member.display_name}"

        rendered_msg = _render_variables(raw_msg, member)
        embed = jarvis_embed(title=title, description=rendered_msg)
        apply_guild_branding(embed, branding, is_premium=status.is_premium)

        file_to_send: discord.File | None = None
        if banner_enabled:
            try:
                avatar_bytes = await member.display_avatar.replace(size=256).read()
            except Exception:
                avatar_bytes = None
            try:
                server_icon_bytes = await guild.icon.replace(size=128).read() if guild.icon else None
            except Exception:
                server_icon_bytes = None

            buf = await render_welcome_goodbye_banner(
                kind=kind,
                username=member.display_name,
                server_name=guild.name,
                member_count=guild.member_count or len(guild.members),
                avatar_bytes=avatar_bytes,
                server_icon_bytes=server_icon_bytes,
                bg_url=bg_url,
                server_logo_url=branding.server_logo_url if status.is_premium else None,
                custom_text=custom_text,
                text_color=text_color,
                accent_color=accent_color,
                text_position=text_pos,
            )
            file_to_send = discord.File(buf, filename=f"{kind}_banner.png")
            embed.set_image(url=f"attachment://{kind}_banner.png")

        if file_to_send is not None:
            await target_channel.send(content=member.mention if kind == "welcome" else None, embed=embed, file=file_to_send)
        else:
            await target_channel.send(content=member.mention if kind == "welcome" else None, embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        cfg = await self.bot.db.get_welcome_settings(member.guild.id)
        if cfg.welcome_enabled and cfg.welcome_channel_id:
            channel = member.guild.get_channel(cfg.welcome_channel_id)
            if isinstance(channel, discord.TextChannel):
                try:
                    await self._dispatch_greeting(member, kind="welcome", target_channel=channel)
                except discord.HTTPException as exc:
                    logger.warning("Failed to send welcome message in %s: %s", member.guild.id, exc)

        if cfg.welcome_dm_enabled and cfg.welcome_dm_message and not member.bot:
            try:
                await member.send(_render_variables(cfg.welcome_dm_message, member))
            except discord.HTTPException:
                pass

    @commands.Cog.listener()
    async def on_member_remove(self, member: discord.Member) -> None:
        cfg = await self.bot.db.get_welcome_settings(member.guild.id)
        if cfg.goodbye_enabled and cfg.goodbye_channel_id:
            channel = member.guild.get_channel(cfg.goodbye_channel_id)
            if isinstance(channel, discord.TextChannel):
                try:
                    await self._dispatch_greeting(member, kind="goodbye", target_channel=channel)
                except discord.HTTPException as exc:
                    logger.warning("Failed to send goodbye message in %s: %s", member.guild.id, exc)

    # ==========================================================================
    # WELCOME & GOODBYE SETUP COMMANDS
    # ==========================================================================
    @commands.hybrid_group(name="welcome", fallback="status", description="Configure server welcome messages & banners.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server")
    async def welcome_group(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        cfg = await self.bot.db.get_welcome_settings(ctx.guild.id)
        ch = f"<#{cfg.welcome_channel_id}>" if cfg.welcome_channel_id else "Not set"
        embed = await self.bot.make_embed(
            ctx.guild.id,
            title="Welcome Configuration",
            description=f"**Enabled:** `{cfg.welcome_enabled}`\n**Channel:** {ch}\n**Message:** {cfg.welcome_message or 'Default'}",
        )
        await ctx.reply(embed=embed, mention_author=False)

    @welcome_group.command(name="channel", description="Set the welcome channel and enable welcome messages.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server")
    async def welcome_channel(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        assert ctx.guild is not None
        await self.bot.db.update_welcome_settings(
            ctx.guild.id, welcome_channel_id=channel.id, welcome_enabled=True
        )
        await ctx.reply(
            embed=success_embed("Welcome Channel Set", f"Welcome banners will be sent to {channel.mention}."),
            mention_author=False,
        )

    @welcome_group.command(name="toggle", description="Enable or disable welcome messages.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server")
    async def welcome_toggle(self, ctx: commands.Context, enabled: bool) -> None:
        assert ctx.guild is not None
        await self.bot.db.update_welcome_settings(ctx.guild.id, welcome_enabled=enabled)
        await ctx.reply(
            embed=success_embed("Welcome Updated", f"Welcome messages are now `{'Enabled' if enabled else 'Disabled'}`."),
            mention_author=False,
        )

    @welcome_group.command(name="test", description="Send a test welcome banner in the current channel.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server")
    async def welcome_test(self, ctx: commands.Context) -> None:
        assert isinstance(ctx.author, discord.Member)
        assert isinstance(ctx.channel, discord.TextChannel)
        await self._dispatch_greeting(ctx.author, kind="welcome", target_channel=ctx.channel)

    @commands.hybrid_group(name="goodbye", fallback="status", description="Configure server goodbye messages & banners.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server")
    async def goodbye_group(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        cfg = await self.bot.db.get_welcome_settings(ctx.guild.id)
        ch = f"<#{cfg.goodbye_channel_id}>" if cfg.goodbye_channel_id else "Not set"
        embed = await self.bot.make_embed(
            ctx.guild.id,
            title="Goodbye Configuration",
            description=f"**Enabled:** `{cfg.goodbye_enabled}`\n**Channel:** {ch}\n**Message:** {cfg.goodbye_message or 'Default'}",
        )
        await ctx.reply(embed=embed, mention_author=False)

    @goodbye_group.command(name="channel", description="Set the goodbye channel and enable goodbye messages.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server")
    async def goodbye_channel(self, ctx: commands.Context, channel: discord.TextChannel) -> None:
        assert ctx.guild is not None
        await self.bot.db.update_welcome_settings(
            ctx.guild.id, goodbye_channel_id=channel.id, goodbye_enabled=True
        )
        await ctx.reply(
            embed=success_embed("Goodbye Channel Set", f"Goodbye banners will be sent to {channel.mention}."),
            mention_author=False,
        )

    @goodbye_group.command(name="toggle", description="Enable or disable goodbye messages.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server")
    async def goodbye_toggle(self, ctx: commands.Context, enabled: bool) -> None:
        assert ctx.guild is not None
        await self.bot.db.update_welcome_settings(ctx.guild.id, goodbye_enabled=enabled)
        await ctx.reply(
            embed=success_embed("Goodbye Updated", f"Goodbye messages are now `{'Enabled' if enabled else 'Disabled'}`."),
            mention_author=False,
        )

    @goodbye_group.command(name="test", description="Send a test goodbye banner in the current channel.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server")
    async def goodbye_test(self, ctx: commands.Context) -> None:
        assert isinstance(ctx.author, discord.Member)
        assert isinstance(ctx.channel, discord.TextChannel)
        await self._dispatch_greeting(ctx.author, kind="goodbye", target_channel=ctx.channel)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(GreetingsCog(bot))
