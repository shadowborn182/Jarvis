"""
JARVIS — Premium, No-Prefix, Custom Branding, Banners & Dashboard Tests
Developer: Shadow
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from config import Settings
from core.banners import render_welcome_goodbye_banner, validate_image_url
from core.branding import apply_guild_branding, jarvis_embed, parse_hex_color
from core.noprefix import NoPrefixService
from core.premium import PremiumService
from dashboard.app import create_dashboard_app
from dashboard.security import SESSION_COOKIE_NAME, DashboardSecurity


@pytest.mark.asyncio
async def test_premium_grant_extend_expire_and_revoke(db_manager) -> None:
    premium = PremiumService(db_manager)
    guild_id = 111222333444
    owner_id = 999000111

    # Initially free
    free_status = await premium.get_guild_status(guild_id)
    assert free_status.is_premium is False

    # Grant 30 days
    granted = await premium.grant_premium(
        guild_id=guild_id,
        actor_id=owner_id,
        plan_name="pro",
        duration=timedelta(days=30),
    )
    assert granted.is_premium is True
    assert granted.plan_key == "pro"

    # Extend by 15 days
    extended = await premium.extend_premium(guild_id, owner_id, timedelta(days=15))
    assert extended.expires_at is not None
    assert extended.expires_at > granted.expires_at  # type: ignore[operator]

    # Enable no-prefix while active, then simulate expiration
    await db_manager.update_guild_branding(guild_id, no_prefix_enabled=True)
    # Force expiry into the past directly in DB to verify auto-expiration
    from sqlalchemy import select
    from database.models import PremiumSubscription

    async with db_manager.session() as session:
        res = await session.execute(
            select(PremiumSubscription).where(
                PremiumSubscription.guild_id == guild_id,
                PremiumSubscription.active.is_(True),
            )
        )
        sub = res.scalar_one()
        sub.expires_at = datetime.now(timezone.utc) - timedelta(minutes=5)

    expiring_soon, newly_expired = await premium.collect_expiring_and_expired()
    assert len(newly_expired) == 1
    assert expiring_soon == []

    after_expire = await premium.get_guild_status(guild_id, bypass_cache=True)
    assert after_expire.is_premium is False

    branding = await db_manager.get_guild_branding(guild_id)
    assert branding.no_prefix_enabled is False

    # Audit log recorded grant, extend, and expire
    logs = await premium.get_guild_audit_logs(guild_id)
    actions = {log.action for log in logs}
    assert {"grant", "extend", "expire"}.issubset(actions)


@pytest.mark.asyncio
async def test_no_prefix_gating_and_conversation_protection(db_manager) -> None:
    premium = PremiumService(db_manager)

    ping_cmd = SimpleNamespace(qualified_name="ping", hidden=False, enabled=True)
    help_cmd = SimpleNamespace(qualified_name="help", hidden=False, enabled=True)
    avatar_cmd = SimpleNamespace(qualified_name="avatar", hidden=False, enabled=True)

    fake_bot = SimpleNamespace(
        db=db_manager,
        premium=premium,
        all_commands={"ping": ping_cmd, "help": help_cmd, "h": help_cmd, "avatar": avatar_cmd, "av": avatar_cmd},
    )
    svc = NoPrefixService(fake_bot)  # type: ignore[arg-type]

    guild_id = 555666777
    await db_manager.ensure_guild(guild_id)

    # Without Premium -> disabled
    assert await svc.is_enabled_for_guild(guild_id) is False

    # With Premium, before enabling -> disabled
    await premium.grant_premium(guild_id, actor_id=1, plan_name="pro", duration=timedelta(days=10))
    assert await svc.is_enabled_for_guild(guild_id) is False

    # Enable No Prefix
    await svc.set_enabled_for_guild(guild_id, True)
    assert await svc.is_enabled_for_guild(guild_id) is True

    # Valid command shapes
    assert svc.looks_like_command("ping", ping_cmd) is True  # type: ignore[arg-type]
    assert svc.looks_like_command("help General", help_cmd) is True  # type: ignore[arg-type]
    assert svc.looks_like_command("avatar @Shadow", avatar_cmd) is True  # type: ignore[arg-type]

    # Normal conversation must NOT trigger
    assert svc.looks_like_command("ping me when you get home", ping_cmd) is False  # type: ignore[arg-type]
    assert svc.looks_like_command("help me with my homework please", help_cmd) is False  # type: ignore[arg-type]
    assert svc.looks_like_command('"ping"', ping_cmd) is False  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_guild_specific_branding_isolation(db_manager) -> None:
    guild_a = 101010101
    guild_b = 202020202

    await db_manager.update_guild_branding(
        guild_a,
        embed_color="#FF5500",
        embed_footer="Alpha Server Footer",
        embed_title_style="uppercase",
    )
    await db_manager.update_guild_branding(
        guild_b,
        embed_color="#00CC88",
        embed_footer="Beta Server Footer",
        embed_title_style="bracketed",
    )

    brand_a = await db_manager.get_guild_branding(guild_a)
    brand_b = await db_manager.get_guild_branding(guild_b)

    assert brand_a.embed_color == "#FF5500"
    assert brand_b.embed_color == "#00CC88"
    assert brand_a.embed_footer != brand_b.embed_footer

    embed_a = jarvis_embed(title="Status", branding=brand_a, is_premium=True)
    embed_b = jarvis_embed(title="Status", branding=brand_b, is_premium=True)
    assert embed_a.title == "STATUS"
    assert embed_b.title == "[ Status ]"
    assert embed_a.color.value == parse_hex_color("#FF5500")[1]  # type: ignore[index,union-attr]
    assert embed_b.color.value == parse_hex_color("#00CC88")[1]  # type: ignore[index,union-attr]


def test_banner_url_validation_and_pillow_render() -> None:
    assert validate_image_url("https://cdn.discordapp.com/icons/1/abc.png")[0] is True
    assert validate_image_url("http://example.com/bg.png")[0] is False
    assert validate_image_url("https://127.0.0.1/secret.png")[0] is False
    assert validate_image_url("https://169.254.169.254/latest/meta-data")[0] is False
    assert validate_image_url("https://example.com/payload.exe")[0] is False


@pytest.mark.asyncio
async def test_pillow_welcome_and_goodbye_png_generation() -> None:
    # Create tiny valid avatar bytes
    avatar_img = Image.new("RGBA", (64, 64), (56, 189, 248, 255))
    av_buf = BytesIO()
    avatar_img.save(av_buf, format="PNG")

    welcome_buf = await render_welcome_goodbye_banner(
        kind="welcome",
        username="Shadow",
        server_name="JARVIS HQ",
        member_count=420,
        avatar_bytes=av_buf.getvalue(),
        custom_text="Welcome {user} to {server}!",
        text_color="#F8FAFC",
        text_position="center",
    )
    assert welcome_buf.getvalue().startswith(b"\x89PNG")

    goodbye_buf = await render_welcome_goodbye_banner(
        kind="goodbye",
        username="Shadow",
        server_name="JARVIS HQ",
        member_count=419,
        text_position="bottom",
    )
    assert goodbye_buf.getvalue().startswith(b"\x89PNG")


def test_dashboard_security_and_guild_isolation(tmp_path) -> None:
    db_file = tmp_path / "dash_test.db"
    cfg = Settings(
        DISCORD_TOKEN="test_token",
        DATABASE_URL=f"sqlite+aiosqlite:///{db_file.as_posix()}",
        SESSION_SECRET="test_session_secret_key",
        CSRF_SECRET="test_csrf_secret_key",
    )
    app = create_dashboard_app(cfg)
    sec = DashboardSecurity(cfg)

    # Permission filter allows Administrator (0x8) or Manage Server (0x20), blocks regular members (0x0)
    filtered = sec.filter_manageable_guilds(
        [
            {"id": "100", "name": "Allowed Guild", "permissions": str(0x20), "owner": False},
            {"id": "200", "name": "Readonly Guild", "permissions": "0", "owner": False},
        ]
    )
    assert [g["id"] for g in filtered] == ["100"]

    with TestClient(app) as client:
        cookie = sec.sign_session(
            {
                "user": {"id": "777", "username": "Shadow", "avatar": None},
                "guilds": [{"id": "100", "name": "Allowed Guild", "owner": True, "permissions": "8"}],
            }
        )
        client.cookies.set(SESSION_COOKIE_NAME, cookie)

        # Authorized guild loads
        resp_ok = client.get("/guild/100")
        assert resp_ok.status_code == 200
        assert "Allowed Guild" in resp_ok.text

        # Unauthorized guild is strictly blocked with 403
        resp_forbidden = client.get("/guild/999999")
        assert resp_forbidden.status_code == 403

        # Health endpoint responds
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["bot"] == "JARVIS"
