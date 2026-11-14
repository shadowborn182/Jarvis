"""
JARVIS — Permanent Branding, Colors, Emojis & Embed Factory
Developer: Shadow
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Final

import discord

from config import BOT_DESCRIPTION, BOT_NAME, DEVELOPER_NAME


class JarvisColors:
    """Dark premium embed color palette for JARVIS."""
    PRIMARY: Final[int] = 0x1E293B     # Deep Slate Accent
    BRAND: Final[int] = 0x38BDF8       # Precision Cyan Blue
    SUCCESS: Final[int] = 0x16A34A     # Emerald Green
    WARNING: Final[int] = 0xD97706     # Amber Warning
    ERROR: Final[int] = 0xDC2626       # Crimson Error
    SECURITY: Final[int] = 0xE11D48    # High-Priority Security Alert
    INFO: Final[int] = 0x0EA5E9        # Informational Sky


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


def _apply_footer(embed: discord.Embed, footer_note: str | None = None) -> discord.Embed:
    base_footer = f"{BOT_NAME} • Developed by {DEVELOPER_NAME}"
    embed.set_footer(text=f"{footer_note} | {base_footer}" if footer_note else base_footer)
    embed.timestamp = datetime.now(timezone.utc)
    return embed


def jarvis_embed(
    title: str | None = None,
    description: str | None = None,
    *,
    color: int = JarvisColors.BRAND,
    footer_note: str | None = None,
) -> discord.Embed:
    """Create a standard dark-themed JARVIS embed."""
    embed = discord.Embed(title=title, description=description, color=color)
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


def get_brand_header() -> str:
    return f"{JarvisEmojis.BRAND} **{BOT_NAME}** — {BOT_DESCRIPTION}"
