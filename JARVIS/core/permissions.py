"""
JARVIS — Role Hierarchy, Server-Owner Protection & Permission Validation
Developer: Shadow
"""

from __future__ import annotations

from typing import Final

import discord

# Permissions that users must NEVER be allowed to grant via Customrole or self-assignable features
DANGEROUS_PERMISSION_FLAGS: Final[tuple[str, ...]] = (
    "administrator",
    "manage_guild",
    "manage_roles",
    "manage_channels",
    "manage_webhooks",
    "ban_members",
    "kick_members",
    "mention_everyone",
    "moderate_members",
    "manage_messages",
    "manage_expressions",
    "view_audit_log",
)


class HierarchyError(Exception):
    """Raised when a moderation or role action violates Discord role hierarchy."""


class BotPermissionError(Exception):
    """Raised when JARVIS lacks required Discord permissions for an action."""


def is_guild_owner(member: discord.Member) -> bool:
    return member.guild.owner_id == member.id


def can_moderate_target(
    actor: discord.Member,
    target: discord.Member,
    *,
    allow_self: bool = False,
) -> tuple[bool, str | None]:
    """
    Validate full Discord role hierarchy and server-owner protection:
    - Never allow moderating the server owner.
    - Never allow moderating self (unless explicitly permitted).
    - Never allow moderating the bot itself via user commands.
    - Actor's top role must be strictly higher than target's top role (unless actor is owner).
    - Bot's top role must be strictly higher than target's top role.
    """
    guild = actor.guild

    if not allow_self and actor.id == target.id:
        return False, "You cannot perform this action on yourself."

    if target.id == guild.owner_id:
        return False, "You cannot perform moderation actions against the server owner."

    if guild.me and target.id == guild.me.id:
        return False, "I cannot perform moderation actions on myself."

    if actor.id != guild.owner_id and actor.top_role <= target.top_role:
        return (
            False,
            f"Your highest role (`{actor.top_role.name}`) must be higher than "
            f"`{target.display_name}`'s highest role (`{target.top_role.name}`).",
        )

    if guild.me and guild.me.top_role <= target.top_role:
        return (
            False,
            f"JARVIS's highest role (`{guild.me.top_role.name}`) must be higher than "
            f"`{target.display_name}`'s highest role (`{target.top_role.name}`).",
        )

    return True, None


def can_manage_role(actor: discord.Member, role: discord.Role) -> tuple[bool, str | None]:
    """Ensure both the actor and JARVIS can safely manage the target role."""
    guild = actor.guild

    if role.is_default():
        return False, "Cannot assign or modify the `@everyone` role."

    if role.managed:
        return False, f"Role `{role.name}` is managed by an external integration or bot."

    if actor.id != guild.owner_id and actor.top_role <= role:
        return False, f"Your highest role must be higher than `{role.name}`."

    if guild.me and guild.me.top_role <= role:
        return False, f"JARVIS's highest role must be higher than `{role.name}`."

    return True, None


def has_dangerous_permissions(permissions: discord.Permissions) -> list[str]:
    """Return any dangerous permission flag names enabled on a Permissions object."""
    flagged: list[str] = []
    for flag in DANGEROUS_PERMISSION_FLAGS:
        if getattr(permissions, flag, False):
            flagged.append(flag)
    return flagged


def strip_dangerous_permissions(permissions: discord.Permissions) -> discord.Permissions:
    """Return a copy of Permissions with all dangerous flags cleared."""
    safe = discord.Permissions(permissions.value)
    kwargs = {flag: False for flag in DANGEROUS_PERMISSION_FLAGS}
    safe.update(**kwargs)
    return safe


def missing_bot_permissions(
    guild: discord.Guild,
    required: list[str],
    channel: discord.abc.GuildChannel | None = None,
) -> list[str]:
    """Check which required permissions JARVIS is missing in the guild or channel."""
    me = guild.me
    if me is None:
        return required

    perms = channel.permissions_for(me) if channel is not None else me.guild_permissions
    return [perm for perm in required if not getattr(perms, perm, False)]
