"""
JARVIS — Per-Server Branding & Banner Customization Commands (Premium)
Developer: Shadow
"""

from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

from core.banners import (
    VALID_TEXT_POSITIONS,
    render_welcome_goodbye_banner,
    validate_image_url,
)
from core.branding import (
    VALID_TITLE_STYLES,
    apply_guild_branding,
    error_embed,
    jarvis_embed,
    parse_hex_color,
    success_embed,
    warning_embed,
)
from core.checks import is_guild_premium
from core.utilities import ConfirmView


def _command_meta(perms: str = "Manage Server", *, is_premium: bool = True, no_prefix: bool = True):
    def decorator(func):
        func.__jarvis_perms__ = perms
        func.__jarvis_premium__ = is_premium
        func.__jarvis_noprefix__ = no_prefix
        return func
    return decorator


class BrandingCog(commands.Cog):
    """Per-guild Premium embed branding and Pillow welcome/goodbye banner customization."""

    category = "Premium"

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.hybrid_group(
        name="brand",
        fallback="view",
        description="Inspect or customize per-server JARVIS Premium branding.",
    )
    @commands.guild_only()
    @_command_meta("Everyone", is_premium=True)
    async def brand_group(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        status = await self.bot.premium.get_guild_status(ctx.guild.id)
        branding = await self.bot.db.get_guild_branding(ctx.guild.id)
        welcome = await self.bot.db.get_welcome_settings(ctx.guild.id)

        embed = jarvis_embed(
            title=f"Server Branding — {ctx.guild.name}",
            description=(
                f"**Premium Status:** `{'Active (' + status.plan_name + ')' if status.is_premium else 'Free Tier'}`\n"
                "*Note: Discord does not allow bots to change their global profile avatar/banner per server. "
                "Server branding customizes embeds, footers, logos, and welcome/goodbye banners.*"
            ),
            branding=branding,
            is_premium=status.is_premium,
        )
        embed.add_field(name="Embed Color", value=f"`{branding.embed_color}`", inline=True)
        embed.add_field(name="Title Style", value=f"`{branding.embed_title_style}`", inline=True)
        embed.add_field(name="Branding Text", value=branding.branding_text or "`Default`", inline=True)
        embed.add_field(name="Custom Footer", value=branding.embed_footer or "`Default (JARVIS • Shadow)`", inline=False)
        embed.add_field(
            name="Welcome Message",
            value=welcome.welcome_message or "`Default`",
            inline=False,
        )
        embed.add_field(
            name="Goodbye Message",
            value=welcome.goodbye_message or "`Default`",
            inline=False,
        )
        await ctx.reply(embed=embed, mention_author=False)

    @brand_group.command(name="color", description="Set this server's custom embed hex color (e.g. #38BDF8).")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    async def brand_color(self, ctx: commands.Context, hex_color: str) -> None:
        assert ctx.guild is not None
        parsed = parse_hex_color(hex_color)
        if parsed is None:
            await ctx.reply(
                embed=error_embed("Invalid Hex Color", "Provide a valid 6-digit hex color like `#38BDF8`."),
                mention_author=False,
            )
            return
        normalized, color_int = parsed
        await self.bot.db.update_guild_branding(ctx.guild.id, embed_color=normalized)
        embed = success_embed("Embed Color Updated", f"Server embed color set to `{normalized}`.")
        embed.color = color_int
        await ctx.reply(embed=embed, mention_author=False)

    @brand_group.command(name="title", description="Set embed title style: default, uppercase, bracketed, or clean.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    async def brand_title(self, ctx: commands.Context, style: str) -> None:
        assert ctx.guild is not None
        cleaned = style.strip().lower()
        if cleaned not in VALID_TITLE_STYLES:
            await ctx.reply(
                embed=error_embed("Invalid Title Style", f"Choose one of: {', '.join(f'`{s}`' for s in VALID_TITLE_STYLES)}"),
                mention_author=False,
            )
            return
        await self.bot.db.update_guild_branding(ctx.guild.id, embed_title_style=cleaned)
        await ctx.reply(
            embed=success_embed("Title Style Updated", f"Embed title style set to `{cleaned}`."),
            mention_author=False,
        )

    @brand_group.command(name="footer", description="Set custom embed footer text and optional HTTPS footer icon URL.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    async def brand_footer(self, ctx: commands.Context, footer_text: str, icon_url: str | None = None) -> None:
        assert ctx.guild is not None
        cleaned_text = footer_text.strip()
        if not cleaned_text or len(cleaned_text) > 200:
            await ctx.reply(embed=error_embed("Invalid Footer", "Footer text must be 1–200 characters."), mention_author=False)
            return
        if icon_url:
            ok, err = validate_image_url(icon_url)
            if not ok:
                await ctx.reply(embed=error_embed("Invalid Icon URL", err or "Invalid URL."), mention_author=False)
                return
        await self.bot.db.update_guild_branding(
            ctx.guild.id,
            embed_footer=cleaned_text,
            footer_icon_url=icon_url.strip() if icon_url else None,
        )
        await ctx.reply(
            embed=success_embed("Footer Updated", f"Custom footer set to `{cleaned_text}`."),
            mention_author=False,
        )

    @brand_group.command(name="icon", description="Set custom server logo URL displayed in branded embeds and banners.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    async def brand_icon(self, ctx: commands.Context, logo_url: str) -> None:
        assert ctx.guild is not None
        ok, err = validate_image_url(logo_url)
        if not ok:
            await ctx.reply(embed=error_embed("Invalid Logo URL", err or "Invalid URL."), mention_author=False)
            return
        await self.bot.db.update_guild_branding(ctx.guild.id, server_logo_url=logo_url.strip())
        await ctx.reply(
            embed=success_embed("Server Logo Updated", "Custom server logo URL saved for embeds and banners."),
            mention_author=False,
        )

    @brand_group.command(name="text", description="Set custom server branding header text displayed on embeds.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    async def brand_text(self, ctx: commands.Context, *, branding_text: str) -> None:
        assert ctx.guild is not None
        cleaned = branding_text.strip()
        if not cleaned or len(cleaned) > 150:
            await ctx.reply(embed=error_embed("Invalid Branding Text", "Must be 1–150 characters."), mention_author=False)
            return
        await self.bot.db.update_guild_branding(ctx.guild.id, branding_text=cleaned)
        await ctx.reply(
            embed=success_embed("Branding Text Updated", f"Embed author branding set to `{cleaned}`."),
            mention_author=False,
        )

    @brand_group.command(
        name="welcome",
        description="Customize welcome message & optional banner settings. Variables: {user}, {mention}, {server}, {member_count}.",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    @app_commands.describe(
        message="Custom welcome message text",
        banner_bg_url="Optional HTTPS PNG/JPG/WEBP background URL",
        text_color="Hex text color (e.g. #F8FAFC)",
        text_position="Vertical position: top, center, or bottom",
    )
    async def brand_welcome(
        self,
        ctx: commands.Context,
        message: str,
        banner_bg_url: str | None = None,
        text_color: str = "#F8FAFC",
        text_position: str = "center",
    ) -> None:
        assert ctx.guild is not None
        parsed_color = parse_hex_color(text_color)
        if parsed_color is None:
            await ctx.reply(embed=error_embed("Invalid Text Color", "Use a hex color like `#F8FAFC`."), mention_author=False)
            return
        pos = text_position.lower()
        if pos not in VALID_TEXT_POSITIONS:
            await ctx.reply(embed=error_embed("Invalid Position", "Position must be `top`, `center`, or `bottom`."), mention_author=False)
            return
        if banner_bg_url:
            ok, err = validate_image_url(banner_bg_url)
            if not ok:
                await ctx.reply(embed=error_embed("Invalid Banner URL", err or "Invalid URL."), mention_author=False)
                return

        await self.bot.db.update_welcome_settings(ctx.guild.id, welcome_message=message.strip())
        await self.bot.db.update_guild_branding(
            ctx.guild.id,
            welcome_banner_enabled=True,
            welcome_banner_text=message.strip()[:250],
            welcome_banner_bg_url=banner_bg_url.strip() if banner_bg_url else None,
            welcome_banner_text_color=parsed_color[0],
            welcome_banner_text_position=pos,
        )
        await ctx.reply(
            embed=success_embed("Welcome Branding Saved", "Custom welcome message and banner configuration saved."),
            mention_author=False,
        )

    @brand_group.command(
        name="goodbye",
        description="Customize goodbye message & optional banner settings.",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @is_guild_premium()
    @_command_meta("Manage Server", is_premium=True)
    async def brand_goodbye(
        self,
        ctx: commands.Context,
        message: str,
        banner_bg_url: str | None = None,
        text_color: str = "#F8FAFC",
        text_position: str = "center",
    ) -> None:
        assert ctx.guild is not None
        parsed_color = parse_hex_color(text_color)
        if parsed_color is None:
            await ctx.reply(embed=error_embed("Invalid Text Color", "Use a hex color like `#F8FAFC`."), mention_author=False)
            return
        pos = text_position.lower()
        if pos not in VALID_TEXT_POSITIONS:
            await ctx.reply(embed=error_embed("Invalid Position", "Position must be `top`, `center`, or `bottom`."), mention_author=False)
            return
        if banner_bg_url:
            ok, err = validate_image_url(banner_bg_url)
            if not ok:
                await ctx.reply(embed=error_embed("Invalid Banner URL", err or "Invalid URL."), mention_author=False)
                return

        await self.bot.db.update_welcome_settings(ctx.guild.id, goodbye_message=message.strip())
        await self.bot.db.update_guild_branding(
            ctx.guild.id,
            goodbye_banner_enabled=True,
            goodbye_banner_text=message.strip()[:250],
            goodbye_banner_bg_url=banner_bg_url.strip() if banner_bg_url else None,
            goodbye_banner_text_color=parsed_color[0],
            goodbye_banner_text_position=pos,
        )
        await ctx.reply(
            embed=success_embed("Goodbye Branding Saved", "Custom goodbye message and banner configuration saved."),
            mention_author=False,
        )

    @brand_group.command(
        name="preview",
        description="Preview this server's custom embed branding and Pillow welcome/goodbye banner.",
    )
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server", is_premium=True)
    async def brand_preview(self, ctx: commands.Context, kind: str = "welcome") -> None:
        assert ctx.guild is not None
        banner_kind = "goodbye" if kind.lower() == "goodbye" else "welcome"
        status = await self.bot.premium.get_guild_status(ctx.guild.id)
        branding = await self.bot.db.get_guild_branding(ctx.guild.id)

        avatar_bytes = await ctx.author.display_avatar.replace(size=256).read()
        server_icon_bytes = await ctx.guild.icon.replace(size=128).read() if ctx.guild.icon else None

        buf = await render_welcome_goodbye_banner(
            kind=banner_kind,
            username=ctx.author.display_name,
            server_name=ctx.guild.name,
            member_count=ctx.guild.member_count or len(ctx.guild.members),
            avatar_bytes=avatar_bytes,
            server_icon_bytes=server_icon_bytes,
            bg_url=branding.welcome_banner_bg_url if banner_kind == "welcome" else branding.goodbye_banner_bg_url,
            server_logo_url=branding.server_logo_url,
            custom_text=branding.welcome_banner_text if banner_kind == "welcome" else branding.goodbye_banner_text,
            text_color=branding.welcome_banner_text_color if banner_kind == "welcome" else branding.goodbye_banner_text_color,
            accent_color=branding.welcome_banner_accent_color if banner_kind == "welcome" else branding.goodbye_banner_accent_color,
            text_position=branding.welcome_banner_text_position if banner_kind == "welcome" else branding.goodbye_banner_text_position,
        )
        file = discord.File(buf, filename=f"{banner_kind}_preview.png")
        embed = jarvis_embed(
            title=f"{banner_kind.title()} Branding Preview",
            description=f"Previewing `{banner_kind}` banner & embed branding for **{ctx.guild.name}**.",
        )
        apply_guild_branding(embed, branding, is_premium=status.is_premium)
        embed.set_image(url=f"attachment://{banner_kind}_preview.png")
        await ctx.reply(embed=embed, file=file, mention_author=False)

    @brand_group.command(name="reset", description="Reset all custom server branding back to JARVIS defaults.")
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    @_command_meta("Manage Server", is_premium=True)
    async def brand_reset(self, ctx: commands.Context) -> None:
        assert ctx.guild is not None
        view = ConfirmView(author_id=ctx.author.id)
        msg = await ctx.reply(
            embed=warning_embed(
                "Confirm Branding Reset",
                f"Reset all custom colors, footers, logos, and banners for **{ctx.guild.name}**?",
            ),
            view=view,
            mention_author=False,
        )
        await view.wait()
        if view.confirmed:
            await self.bot.db.reset_guild_branding(ctx.guild.id)
            await self.bot.noprefix.invalidate(ctx.guild.id)
            await msg.edit(
                embed=success_embed("Branding Reset", f"Branding for **{ctx.guild.name}** restored to defaults."),
                view=view,
            )
        else:
            await msg.edit(embed=warning_embed("Cancelled", "Branding reset cancelled."), view=view)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(BrandingCog(bot))
