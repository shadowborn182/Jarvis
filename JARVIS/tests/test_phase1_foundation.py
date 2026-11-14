"""
JARVIS — Phase 1 Foundation Tests (Identity, Config, Hierarchy, Utilities, Cache, DB)
Developer: Shadow
"""

from __future__ import annotations

from datetime import timedelta
from types import SimpleNamespace

import discord
import pytest

from config import BOT_DESCRIPTION, BOT_NAME, DEVELOPER_NAME, OFFICIAL_CATEGORIES, Settings
from core.cache import AsyncTTLCache
from core.permissions import (
    can_moderate_target,
    has_dangerous_permissions,
    strip_dangerous_permissions,
)
from core.utilities import format_duration, parse_duration, truncate_text


def test_permanent_identity() -> None:
    assert BOT_NAME == "JARVIS"
    assert DEVELOPER_NAME == "Shadow"
    assert "All-In-One" in BOT_DESCRIPTION
    assert len(OFFICIAL_CATEGORIES) == 17


def test_settings_prefix_validation() -> None:
    cfg = Settings(DEFAULT_PREFIX=" ! ")
    assert cfg.default_prefix == "!"
    with pytest.raises(ValueError):
        Settings(DEFAULT_PREFIX="prefix_longer_than_ten")


def test_duration_parsing_and_formatting() -> None:
    assert parse_duration("10m") == timedelta(minutes=10)
    assert parse_duration("2h 30m") == timedelta(hours=2, minutes=30)
    assert parse_duration("1w") == timedelta(days=7)
    assert parse_duration("invalid") is None
    assert parse_duration("0s") is None
    assert format_duration(3661) == "1h 1m 1s"
    assert truncate_text("hello world", 8) == "hello..."


def test_role_hierarchy_and_owner_protection() -> None:
    bot_member = SimpleNamespace(id=999, top_role=50)
    guild = SimpleNamespace(owner_id=1, me=bot_member)

    owner = SimpleNamespace(id=1, guild=guild, top_role=100, display_name="Owner")
    admin = SimpleNamespace(id=2, guild=guild, top_role=40, display_name="Admin")
    mod = SimpleNamespace(id=3, guild=guild, top_role=20, display_name="Mod")
    member = SimpleNamespace(id=4, guild=guild, top_role=10, display_name="Member")

    # Cannot moderate server owner
    ok, msg = can_moderate_target(admin, owner)
    assert not ok and "owner" in (msg or "").lower()

    # Cannot moderate self
    ok, _ = can_moderate_target(admin, admin)
    assert not ok

    # Lower role cannot moderate higher role
    ok, _ = can_moderate_target(mod, admin)
    assert not ok

    # Higher role can moderate lower role when bot role is above target
    ok, msg = can_moderate_target(admin, member)
    assert ok and msg is None


def test_dangerous_permissions_stripped() -> None:
    perms = discord.Permissions(administrator=True, send_messages=True, manage_roles=True)
    flagged = has_dangerous_permissions(perms)
    assert "administrator" in flagged
    assert "manage_roles" in flagged

    safe = strip_dangerous_permissions(perms)
    assert not safe.administrator
    assert not safe.manage_roles
    assert safe.send_messages


@pytest.mark.asyncio
async def test_async_ttl_cache() -> None:
    cache: AsyncTTLCache[int, str] = AsyncTTLCache(ttl_seconds=60.0)
    await cache.set(12345, "?")
    assert await cache.get(12345) == "?"
    await cache.invalidate(12345)
    assert await cache.get(12345) is None


@pytest.mark.asyncio
async def test_database_guild_prefix_persistence(db_manager) -> None:
    assert await db_manager.health_check() is True
    await db_manager.ensure_guild(777888999)
    assert await db_manager.get_guild_prefix(777888999) == "j!"

    await db_manager.set_guild_prefix(777888999, "!")
    assert await db_manager.get_guild_prefix(777888999) == "!"
