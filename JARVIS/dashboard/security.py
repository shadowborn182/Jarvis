"""
JARVIS Dashboard — Signed Sessions, CSRF Protection & Discord OAuth2 Permissions
Developer: Shadow
"""

from __future__ import annotations

import hmac
import secrets
from typing import Any

from fastapi import Request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from config import Settings

SESSION_COOKIE_NAME = "jarvis_session"
SESSION_MAX_AGE = 60 * 60 * 24 * 7  # 7 days

# Discord permission bits
PERM_ADMINISTRATOR = 0x8
PERM_MANAGE_GUILD = 0x20


class DashboardSecurity:
    """Manages signed session cookies, OAuth state tokens, CSRF tokens, and guild permissions."""

    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.serializer = URLSafeTimedSerializer(settings.session_secret, salt="jarvis-session")
        self.csrf_serializer = URLSafeTimedSerializer(settings.csrf_secret, salt="jarvis-csrf")

    def sign_session(self, payload: dict[str, Any]) -> str:
        return self.serializer.dumps(payload)

    def read_session(self, request: Request) -> dict[str, Any] | None:
        token = request.cookies.get(SESSION_COOKIE_NAME)
        if not token:
            return None
        try:
            data = self.serializer.loads(token, max_age=SESSION_MAX_AGE)
            return data if isinstance(data, dict) else None
        except (BadSignature, SignatureExpired):
            return None

    def generate_oauth_state(self) -> str:
        return self.serializer.dumps({"nonce": secrets.token_urlsafe(16), "purpose": "oauth"})

    def verify_oauth_state(self, state: str) -> bool:
        try:
            data = self.serializer.loads(state, max_age=600)
            return isinstance(data, dict) and data.get("purpose") == "oauth"
        except (BadSignature, SignatureExpired):
            return False

    def generate_csrf(self, user_id: str) -> str:
        return self.csrf_serializer.dumps({"uid": str(user_id), "nonce": secrets.token_hex(8)})

    def verify_csrf(self, token: str, user_id: str) -> bool:
        if not token:
            return False
        try:
            data = self.csrf_serializer.loads(token, max_age=3600 * 6)
            return isinstance(data, dict) and hmac.compare_digest(str(data.get("uid", "")), str(user_id))
        except (BadSignature, SignatureExpired):
            return False

    @staticmethod
    def has_manage_guild_permission(permissions_raw: str | int) -> bool:
        try:
            perms = int(permissions_raw)
        except (TypeError, ValueError):
            return False
        return bool((perms & PERM_ADMINISTRATOR) or (perms & PERM_MANAGE_GUILD))

    @classmethod
    def filter_manageable_guilds(cls, guilds: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Return only guilds where the user is owner or has Administrator / Manage Server."""
        manageable: list[dict[str, Any]] = []
        for g in guilds:
            if g.get("owner") or cls.has_manage_guild_permission(g.get("permissions", 0)):
                manageable.append(g)
        return manageable
