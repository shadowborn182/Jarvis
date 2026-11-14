"""
JARVIS — Permanent Branding, Per-Guild Embed Customization & Embed Factory
Developer: Shadow
"""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Final

import discord

from config import BOT_DESCRIPTION, BOT_NAME, DEVELOPER_NAME

if TYPE_CHECKING:
    from database.models import GuildBranding

HEX_COLOR_RE = re.compile(r"^#?([0-9a-fA-F]{6})$")
VALID_TITLE_STYLES: Final[tuple[str, ...]] = ("default", "uppercase", "bracketed", "clean")


class JarvisColors:
    """Dark premium embed color palette for JARVIS."""
    PRIMARY: Final[int] = 0x1E293B     # Deep Slate Accent
    BRAND: Final[int] = 0x38BDF8       # Precision Cyan Blue
    SUCCESS: Final[int] = 0x16A34A     # Emerald Green
    WARNING: Final[int] = 0xD97706     # Amber Warning
    ERROR: Final[int] = 0xDC2626       # Crimson Error
    SECURITY: Final[int] = 0xE11D48    # High-Priority Security Alert
    INFO: Final[int] = 0x0EA5E9        # Informational Sky
    PREMIUM: Final[int] = 0xF59E0B     # Amber Gold Premium Accent


class JarvisEmojis:
    """Consistent Unicode + configurable custom emoji tokens for JARVIS."""
    BRAND: Final[str] = "⚡"
    SUCCESS: Final[str] = "✅"
    ERROR: Final[str] = "❌"
    WARNING: Final[str] = "⚠️"
    SECURITY: Final[str] = "🛡️"
    INFO: Final[str] = "ℹ️"
    PREFIX: Final[str] = "⌨️"
    CROWN: Final[str] = "👑"
    PREMIUM: Final[str] = "💎"
    NOPREFIX: Final[str] = "⚡"
    MUSIC: Final[str] = "🎵"
    TICKET: Final[str] = "🎫"
    GIVEAWAY: Final[str] = "🎉"
    LOCK: Final[str] = "🔒"
    UNLOCK: Final[str] = "🔓"

    CATEGORY_MAP: Final[dict[str, str]] = {
        "Security": "🛡️",
        "Utility": "🧰",
        "General": "⚡",
        "Moderation": "🔨",
        "Autoroles": "🎭",
        "Fun": "🎲",
        "Greetings": "👋",
        "Giveaway": "🎉",
        "Ticket": "🎫",
        "Music": "🎵",
        "Tracker": "📈",
        "Logging": "📜",
        "Birthdays": "🎂",
        "Customrole": "🎨",
        "Template": "📐",
        "Marriage": "💍",
        "Premium": "💎",
    }


def parse_hex_color(value: str) -> tuple[str, int] | None:
    """Validate and normalize a hex color string like '#38BDF8' -> ('#38BDF8', 0x38BDF8)."""
    match = HEX_COLOR_RE.match(value.strip())
    if not match:
        return None
    hex_digits = match.group(1).upper()
    return f"#{hex_digits}", int(hex_digits, 16)


def format_branded_title(title: str | None, style: str = "default") -> str | None:
    if not title:
        return title
    if style == "uppercase":
        return title.upper()
    if style == "bracketed":
        return f"[ {title} ]"
    if style == "clean":
        # Strip leading decorative emojis if present
        return title.lstrip("⚡✅❌⚠️🛡️ℹ️💎👑 ").strip() or title
    return title


def _apply_footer(
    embed: discord.Embed,
    footer_note: str | None = None,
    *,
    custom_footer: str | None = None,
    footer_icon_url: str | None = None,
) -> discord.Embed:
    base_footer = custom_footer.strip() if custom_footer and custom_footer.strip() else f"{BOT_NAME} • Developed by {DEVELOPER_NAME}"
    text = f"{footer_note} | {base_footer}" if footer_note else base_footer
    if footer_icon_url:
        embed.set_footer(text=text[:2048], icon_url=footer_icon_url)
    else:
        embed.set_footer(text=text[:2048])
    embed.timestamp = datetime.now(timezone.utc)
    return embed


def apply_guild_branding(
    embed: discord.Embed,
    branding: GuildBranding | None,
    *,
    is_premium: bool = False,
    footer_note: str | None = None,
    override_color: bool = True,
) -> discord.Embed:
    """Apply per-guild Premium branding (embed color, title style, footer, icon, server logo, branding text)."""
    if branding is None or not is_premium:
        return _apply_footer(embed, footer_note)

    if override_color and branding.embed_color:
        parsed = parse_hex_color(branding.embed_color)
        if parsed is not None:
            embed.color = parsed[1]

    if embed.title:
        embed.title = format_branded_title(embed.title, branding.embed_title_style)

    if branding.server_logo_url:
        embed.set_thumbnail(url=branding.server_logo_url)

    if branding.branding_text and not embed.author.name:
        embed.set_author(
            name=branding.branding_text[:256],
            icon_url=branding.server_logo_url or None,
        )

    return _apply_footer(
        embed,
        footer_note=footer_note,
        custom_footer=branding.embed_footer,
        footer_icon_url=branding.footer_icon_url,
    )


def jarvis_embed(
    title: str | None = None,
    description: str | None = None,
    *,
    color: int = JarvisColors.BRAND,
    footer_note: str | None = None,
    branding: GuildBranding | None = None,
    is_premium: bool = False,
) -> discord.Embed:
    """Create a standard dark-themed JARVIS embed with optional Premium per-guild branding."""
    embed = discord.Embed(title=title, description=description, color=color)
    if branding is not None and is_premium:
        return apply_guild_branding(embed, branding, is_premium=True, footer_note=footer_note)
    return _apply_footer(embed, footer_note)


def success_embed(
    title: str,
    description: str | None = None,
    *,
    footer_note: str | None = None,
) -> discord.Embed:
    return jarvis_embed(
        title=f"{JarvisEmojis.SUCCESS} {title}",
        description=description,
        color=JarvisColors.SUCCESS,
        footer_note=footer_note,
    )


def error_embed(
    title: str,
    description: str | None = None,
    *,
    footer_note: str | None = None,
) -> discord.Embed:
    return jarvis_embed(
        title=f"{JarvisEmojis.ERROR} {title}",
        description=description,
        color=JarvisColors.ERROR,
        footer_note=footer_note,
    )


def warning_embed(
    title: str,
    description: str | None = None,
    *,
    footer_note: str | None = None,
) -> discord.Embed:
    return jarvis_embed(
        title=f"{JarvisEmojis.WARNING} {title}",
        description=description,
        color=JarvisColors.WARNING,
        footer_note=footer_note,
    )


def security_embed(
    title: str,
    description: str | None = None,
    *,
    footer_note: str | None = None,
) -> discord.Embed:
    return jarvis_embed(
        title=f"{JarvisEmojis.SECURITY} {title}",
        description=description,
        color=JarvisColors.SECURITY,
        footer_note=footer_note,
    )


def info_embed(
    title: str,
    description: str | None = None,
    *,
    footer_note: str | None = None,
) -> discord.Embed:
    return jarvis_embed(
        title=f"{JarvisEmojis.INFO} {title}",
        description=description,
        color=JarvisColors.INFO,
        footer_note=footer_note,
    )


def premium_embed(
    title: str,
    description: str | None = None,
    *,
    footer_note: str | None = None,
) -> discord.Embed:
    return jarvis_embed(
        title=f"{JarvisEmojis.PREMIUM} {title}",
        description=description,
        color=JarvisColors.PREMIUM,
        footer_note=footer_note,
    )


def get_brand_header() -> str:
    return f"{JarvisEmojis.BRAND} **{BOT_NAME}** — {BOT_DESCRIPTION}"
