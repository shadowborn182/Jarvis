"""
JARVIS — FastAPI Premium Web Dashboard
Developer: Shadow
"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import aiohttp
from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from config import BOT_DESCRIPTION, BOT_NAME, DEVELOPER_NAME, Settings, get_settings
from core.banners import VALID_TEXT_POSITIONS, render_welcome_goodbye_banner, validate_image_url
from core.branding import VALID_TITLE_STYLES, parse_hex_color
from core.database import DatabaseManager
from core.premium import PremiumService
from dashboard.security import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE,
    DashboardSecurity,
)

logger = logging.getLogger("JARVIS.Dashboard")

DASHBOARD_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = DASHBOARD_DIR / "templates"
STATIC_DIR = DASHBOARD_DIR / "static"

DISCORD_API_BASE = "https://discord.com/api/v10"
DISCORD_OAUTH_AUTHORIZE = "https://discord.com/oauth2/authorize"
DISCORD_OAUTH_TOKEN = "https://discord.com/api/oauth2/token"


class DashboardState:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.db = DatabaseManager(settings)
        self.premium = PremiumService(self.db)
        self.security = DashboardSecurity(settings)


def create_dashboard_app(settings: Settings | None = None) -> FastAPI:
    cfg = settings or get_settings()
    state = DashboardState(cfg)

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        await state.db.init_models()
        yield
        await state.db.close()

    app = FastAPI(title=f"{BOT_NAME} Dashboard", lifespan=lifespan)
    app.state.jarvis = state

    if STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

    templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

    def _base_ctx(request: Request, user: dict[str, Any] | None = None) -> dict[str, Any]:
        return {
            "request": request,
            "bot_name": BOT_NAME,
            "developer_name": DEVELOPER_NAME,
            "bot_description": BOT_DESCRIPTION,
            "user": user,
        }

    def _require_user(request: Request) -> dict[str, Any]:
        session = state.security.read_session(request)
        if not session or not session.get("user"):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
        return session

    def _assert_guild_access(session: dict[str, Any], guild_id: int) -> dict[str, Any]:
        guilds = session.get("guilds", [])
        match = next((g for g in guilds if str(g.get("id")) == str(guild_id)), None)
        if match is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have Manage Server permission for this guild.",
            )
        return match

    # ==========================================================================
    # HEALTH & AUTH ROUTES
    # ==========================================================================
    @app.get("/health")
    async def health() -> dict[str, Any]:
        db_ok = await state.db.health_check()
        return {"status": "ok" if db_ok else "degraded", "bot": BOT_NAME, "developer": DEVELOPER_NAME}

    @app.get("/", response_class=HTMLResponse)
    async def home(request: Request):
        session = state.security.read_session(request)
        if session and session.get("user"):
            return RedirectResponse(url="/servers", status_code=status.HTTP_302_FOUND)
        oauth_configured = bool(cfg.discord_client_id and cfg.discord_client_secret)
        return templates.TemplateResponse(
            request,
            "login.html",
            {**_base_ctx(request), "oauth_configured": oauth_configured},
        )

    @app.get("/auth/login")
    async def auth_login():
        if not cfg.discord_client_id or not cfg.discord_client_secret:
            raise HTTPException(
                status_code=503,
                detail="Discord OAuth2 credentials (DISCORD_CLIENT_ID / DISCORD_CLIENT_SECRET) are not configured in .env.",
            )
        oauth_state = state.security.generate_oauth_state()
        params = urlencode(
            {
                "client_id": cfg.discord_client_id,
                "redirect_uri": cfg.discord_redirect_uri,
                "response_type": "code",
                "scope": "identify guilds",
                "state": oauth_state,
            }
        )
        return RedirectResponse(url=f"{DISCORD_OAUTH_AUTHORIZE}?{params}")

    @app.get("/auth/callback")
    async def oauth_callback(code: str = "", state: str = ""):
        if not code or not state or not app.state.jarvis.security.verify_oauth_state(state):
            raise HTTPException(status_code=400, detail="Invalid or expired OAuth2 state.")

        timeout = aiohttp.ClientTimeout(total=10)
        async with aiohttp.ClientSession(timeout=timeout) as http:
            token_resp = await http.post(
                DISCORD_OAUTH_TOKEN,
                data={
                    "client_id": cfg.discord_client_id,
                    "client_secret": cfg.discord_client_secret,
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": cfg.discord_redirect_uri,
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
            )
            if token_resp.status != 200:
                raise HTTPException(status_code=401, detail="Failed to exchange Discord OAuth2 code.")
            token_data = await token_resp.json()
            access_token = token_data.get("access_token")
            if not access_token:
                raise HTTPException(status_code=401, detail="Missing Discord access token.")

            headers = {"Authorization": f"Bearer {access_token}"}
            user_resp = await http.get(f"{DISCORD_API_BASE}/users/@me", headers=headers)
            guilds_resp = await http.get(f"{DISCORD_API_BASE}/users/@me/guilds", headers=headers)
            if user_resp.status != 200 or guilds_resp.status != 200:
                raise HTTPException(status_code=401, detail="Failed to fetch Discord user profile/guilds.")

            user_json = await user_resp.json()
            guilds_json = await guilds_resp.json()

        manageable = app.state.jarvis.security.filter_manageable_guilds(guilds_json)
        compact_guilds = [
            {
                "id": str(g["id"]),
                "name": g.get("name", "Unnamed Server"),
                "icon": g.get("icon"),
                "owner": bool(g.get("owner", False)),
                "permissions": str(g.get("permissions", "0")),
            }
            for g in manageable
        ]
        session_payload = {
            "user": {
                "id": str(user_json["id"]),
                "username": user_json.get("username", "User"),
                "avatar": user_json.get("avatar"),
            },
            "guilds": compact_guilds,
        }
        cookie_val = app.state.jarvis.security.sign_session(session_payload)
        resp = RedirectResponse(url="/servers", status_code=status.HTTP_302_FOUND)
        resp.set_cookie(
            key=SESSION_COOKIE_NAME,
            value=cookie_val,
            max_age=SESSION_MAX_AGE,
            httponly=True,
            samesite="lax",
            secure=cfg.is_production,
        )
        return resp

    @app.post("/auth/logout")
    async def auth_logout():
        resp = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
        resp.delete_cookie(SESSION_COOKIE_NAME)
        return resp

    # ==========================================================================
    # SERVER LIST & PER-GUILD CONFIGURATION ROUTES
    # ==========================================================================
    @app.get("/servers", response_class=HTMLResponse)
    async def server_list(request: Request):
        session = state.security.read_session(request)
        if not session or not session.get("user"):
            return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

        enriched: list[dict[str, Any]] = []
        for g in session.get("guilds", []):
            gid = int(g["id"])
            prem = await state.premium.get_guild_status(gid)
            enriched.append(
                {
                    **g,
                    "is_premium": prem.is_premium,
                    "plan_name": prem.plan_name,
                    "expires_at": prem.expires_at.strftime("%Y-%m-%d %H:%M UTC") if prem.expires_at else ("Lifetime" if prem.is_premium else "Free"),
                }
            )

        csrf_token = state.security.generate_csrf(session["user"]["id"])
        return templates.TemplateResponse(
            request,
            "servers.html",
            {**_base_ctx(request, session["user"]), "guilds": enriched, "csrf_token": csrf_token},
        )

    @app.get("/guild/{guild_id}", response_class=HTMLResponse)
    async def guild_dashboard(request: Request, guild_id: int, saved: str = "", error: str = ""):
        session = _require_user(request)
        guild_meta = _assert_guild_access(session, guild_id)

        prefix = await state.db.get_guild_prefix(guild_id)
        prem = await state.premium.get_guild_status(guild_id, bypass_cache=True)
        branding = await state.db.get_guild_branding(guild_id)
        welcome = await state.db.get_welcome_settings(guild_id)
        csrf_token = state.security.generate_csrf(session["user"]["id"])

        return templates.TemplateResponse(
            request,
            "guild.html",
            {
                **_base_ctx(request, session["user"]),
                "guild": guild_meta,
                "guild_id": guild_id,
                "prefix": prefix,
                "premium": prem,
                "branding": branding,
                "welcome": welcome,
                "csrf_token": csrf_token,
                "saved": saved,
                "error": error,
                "title_styles": VALID_TITLE_STYLES,
                "text_positions": VALID_TEXT_POSITIONS,
            },
        )

    @app.post("/guild/{guild_id}/settings")
    async def save_guild_settings(
        request: Request,
        guild_id: int,
        csrf_token: str = Form(...),
        prefix: str = Form("j!"),
        no_prefix_enabled: str | None = Form(None),
        embed_color: str = Form("#38BDF8"),
        embed_title_style: str = Form("default"),
        embed_footer: str = Form(""),
        footer_icon_url: str = Form(""),
        server_logo_url: str = Form(""),
        branding_text: str = Form(""),
        welcome_message: str = Form(""),
        welcome_banner_enabled: str | None = Form(None),
        welcome_banner_bg_url: str = Form(""),
        welcome_banner_text: str = Form(""),
        welcome_banner_text_color: str = Form("#F8FAFC"),
        welcome_banner_text_position: str = Form("center"),
        goodbye_message: str = Form(""),
        goodbye_banner_enabled: str | None = Form(None),
        goodbye_banner_bg_url: str = Form(""),
        goodbye_banner_text: str = Form(""),
        goodbye_banner_text_color: str = Form("#F8FAFC"),
        goodbye_banner_text_position: str = Form("center"),
    ):
        session = _require_user(request)
        _assert_guild_access(session, guild_id)
        if not state.security.verify_csrf(csrf_token, session["user"]["id"]):
            raise HTTPException(status_code=403, detail="Invalid CSRF token.")

        cleaned_prefix = prefix.strip()
        if not cleaned_prefix or len(cleaned_prefix) > 10 or " " in cleaned_prefix:
            return RedirectResponse(
                url=f"/guild/{guild_id}?error=Invalid+prefix+(1-10+chars,+no+spaces)",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        await state.db.set_guild_prefix(guild_id, cleaned_prefix)

        prem = await state.premium.get_guild_status(guild_id, bypass_cache=True)
        if not prem.is_premium:
            # Non-premium servers can still update prefix and standard welcome/goodbye text
            await state.db.update_welcome_settings(
                guild_id,
                welcome_message=welcome_message.strip() or None,
                goodbye_message=goodbye_message.strip() or None,
            )
            return RedirectResponse(
                url=f"/guild/{guild_id}?saved=Standard+settings+saved.+Upgrade+to+Premium+for+No-Prefix+and+custom+branding.",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        # Validate Premium fields
        color_norm = parse_hex_color(embed_color)
        w_color_norm = parse_hex_color(welcome_banner_text_color)
        g_color_norm = parse_hex_color(goodbye_banner_text_color)
        if not color_norm or not w_color_norm or not g_color_norm:
            return RedirectResponse(
                url=f"/guild/{guild_id}?error=Invalid+hex+color+value",
                status_code=status.HTTP_303_SEE_OTHER,
            )

        for label, url_val in (
            ("Footer icon URL", footer_icon_url.strip()),
            ("Server logo URL", server_logo_url.strip()),
            ("Welcome banner background", welcome_banner_bg_url.strip()),
            ("Goodbye banner background", goodbye_banner_bg_url.strip()),
        ):
            if url_val:
                ok, err = validate_image_url(url_val)
                if not ok:
                    return RedirectResponse(
                        url=f"/guild/{guild_id}?error={label}:+{err}",
                        status_code=status.HTTP_303_SEE_OTHER,
                    )

        style = embed_title_style if embed_title_style in VALID_TITLE_STYLES else "default"
        w_pos = welcome_banner_text_position if welcome_banner_text_position in VALID_TEXT_POSITIONS else "center"
        g_pos = goodbye_banner_text_position if goodbye_banner_text_position in VALID_TEXT_POSITIONS else "center"

        await state.db.update_welcome_settings(
            guild_id,
            welcome_message=welcome_message.strip() or None,
            goodbye_message=goodbye_message.strip() or None,
        )
        await state.db.update_guild_branding(
            guild_id,
            no_prefix_enabled=bool(no_prefix_enabled),
            embed_color=color_norm[0],
            embed_title_style=style,
            embed_footer=embed_footer.strip()[:250] or None,
            footer_icon_url=footer_icon_url.strip() or None,
            server_logo_url=server_logo_url.strip() or None,
            branding_text=branding_text.strip()[:250] or None,
            welcome_banner_enabled=bool(welcome_banner_enabled),
            welcome_banner_bg_url=welcome_banner_bg_url.strip() or None,
            welcome_banner_text=welcome_banner_text.strip()[:250] or None,
            welcome_banner_text_color=w_color_norm[0],
            welcome_banner_text_position=w_pos,
            goodbye_banner_enabled=bool(goodbye_banner_enabled),
            goodbye_banner_bg_url=goodbye_banner_bg_url.strip() or None,
            goodbye_banner_text=goodbye_banner_text.strip()[:250] or None,
            goodbye_banner_text_color=g_color_norm[0],
            goodbye_banner_text_position=g_pos,
        )

        return RedirectResponse(
            url=f"/guild/{guild_id}?saved=Premium+settings+saved+successfully",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    @app.post("/guild/{guild_id}/reset")
    async def reset_guild_settings(
        request: Request,
        guild_id: int,
        csrf_token: str = Form(...),
    ):
        session = _require_user(request)
        _assert_guild_access(session, guild_id)
        if not state.security.verify_csrf(csrf_token, session["user"]["id"]):
            raise HTTPException(status_code=403, detail="Invalid CSRF token.")

        await state.db.reset_guild_branding(guild_id)
        return RedirectResponse(
            url=f"/guild/{guild_id}?saved=Branding+reset+to+JARVIS+defaults",
            status_code=status.HTTP_303_SEE_OTHER,
        )

    @app.get("/api/guild/{guild_id}/banner-preview")
    async def banner_preview(request: Request, guild_id: int, kind: str = "welcome"):
        session = _require_user(request)
        guild_meta = _assert_guild_access(session, guild_id)
        branding = await state.db.get_guild_branding(guild_id)
        banner_kind = "goodbye" if kind == "goodbye" else "welcome"

        buf = await render_welcome_goodbye_banner(
            kind=banner_kind,
            username=session["user"]["username"],
            server_name=guild_meta.get("name", "Discord Server"),
            member_count=128,
            bg_url=branding.welcome_banner_bg_url if banner_kind == "welcome" else branding.goodbye_banner_bg_url,
            server_logo_url=branding.server_logo_url,
            custom_text=branding.welcome_banner_text if banner_kind == "welcome" else branding.goodbye_banner_text,
            text_color=branding.welcome_banner_text_color if banner_kind == "welcome" else branding.goodbye_banner_text_color,
            accent_color=branding.welcome_banner_accent_color if banner_kind == "welcome" else branding.goodbye_banner_accent_color,
            text_position=branding.welcome_banner_text_position if banner_kind == "welcome" else branding.goodbye_banner_text_position,
        )
        return StreamingResponse(buf, media_type="image/png")

    return app


app = create_dashboard_app()
