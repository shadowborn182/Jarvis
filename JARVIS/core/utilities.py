"""
JARVIS — Shared Utilities, Duration Parsing, Safe Truncation & Confirmation Views
Developer: Shadow
"""

from __future__ import annotations

import re
from datetime import timedelta

import discord

from core.branding import error_embed

_DURATION_PATTERN = re.compile(r"(?P<value>\d+)\s*(?P<unit>[smhdw])", re.IGNORECASE)

_UNIT_SECONDS = {
    "s": 1,
    "m": 60,
    "h": 3600,
    "d": 86400,
    "w": 604800,
}


def parse_duration(raw: str) -> timedelta | None:
    """
    Parse compact human duration strings like '10m', '2h30m', '7d', '1w'.
    Returns None if the string is invalid or zero/negative.
    """
    cleaned = raw.strip()
    if not cleaned:
        return None

    matches = list(_DURATION_PATTERN.finditer(cleaned))
    if not matches:
        return None

    # Verify the entire string consisted of valid duration tokens (no garbage)
    reconstructed = "".join(m.group(0) for m in matches).replace(" ", "")
    if reconstructed.lower() != cleaned.replace(" ", "").lower():
        return None

    total_seconds = 0
    for match in matches:
        value = int(match.group("value"))
        unit = match.group("unit").lower()
        total_seconds += value * _UNIT_SECONDS[unit]

    if total_seconds <= 0:
        return None
    return timedelta(seconds=total_seconds)


def format_duration(seconds: float | int) -> str:
    """Format seconds into a crisp human-readable string like '2d 4h 12m 5s'."""
    total = max(0, int(seconds))
    days, rem = divmod(total, 86400)
    hours, rem = divmod(rem, 3600)
    minutes, secs = divmod(rem, 60)

    parts: list[str] = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes:
        parts.append(f"{minutes}m")
    if secs or not parts:
        parts.append(f"{secs}s")
    return " ".join(parts)


def truncate_text(text: str, limit: int = 1024) -> str:
    """Safely truncate text to respect Discord embed field limits."""
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 3)] + "..."


class ConfirmView(discord.ui.View):
    """Reusable confirmation prompt view for destructive or bulk operations."""

    def __init__(self, author_id: int, timeout: float = 45.0) -> None:
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.confirmed: bool | None = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                embed=error_embed("Not Allowed", "Only the command invoker can confirm this action."),
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.danger)
    async def confirm_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        self.confirmed = True
        for child in self.children:
            child.disabled = True  # type: ignore[attr-defined]
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(
        self, interaction: discord.Interaction, _button: discord.ui.Button
    ) -> None:
        self.confirmed = False
        for child in self.children:
            child.disabled = True  # type: ignore[attr-defined]
        await interaction.response.edit_message(view=self)
        self.stop()
