"""
JARVIS — Central Configuration & Permanent Identity Module
Developer: Shadow
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Final

from dotenv import load_dotenv
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Project root directory (JARVIS/)
BASE_DIR: Final[Path] = Path(__file__).resolve().parent
LOGS_DIR: Final[Path] = BASE_DIR / "logs"
ASSETS_DIR: Final[Path] = BASE_DIR / "assets"
DATABASE_DIR: Final[Path] = BASE_DIR / "database"

# Ensure critical local directories exist
LOGS_DIR.mkdir(parents=True, exist_ok=True)
DATABASE_DIR.mkdir(parents=True, exist_ok=True)
(DATABASE_DIR / "backups").mkdir(parents=True, exist_ok=True)

# Load .env cleanly if present
load_dotenv(BASE_DIR / ".env")

# ==============================================================================
# PERMANENT IDENTITY CONSTANTS (IMMUTABLE)
# ==============================================================================
BOT_NAME: Final[str] = "JARVIS"
DEVELOPER_NAME: Final[str] = "Shadow"
BOT_DESCRIPTION: Final[str] = "Advanced All-In-One Discord Management Bot"
BOT_VERSION: Final[str] = "1.0.0"

# ==============================================================================
# 17 OFFICIAL MODULE CATEGORIES
# ==============================================================================
OFFICIAL_CATEGORIES: Final[tuple[str, ...]] = (
    "Security",
    "Utility",
    "General",
    "Moderation",
    "Autoroles",
    "Fun",
    "Greetings",
    "Giveaway",
    "Ticket",
    "Music",
    "Tracker",
    "Logging",
    "Birthdays",
    "Customrole",
    "Template",
    "Marriage",
    "Premium",
)


class Settings(BaseSettings):
    """Validated runtime settings loaded from environment variables and .env."""

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # Discord credentials
    discord_token: str = Field(default="", alias="DISCORD_TOKEN")
    discord_client_id: str = Field(default="", alias="DISCORD_CLIENT_ID")
    discord_client_secret: str = Field(default="", alias="DISCORD_CLIENT_SECRET")
    bot_owner_ids_raw: str = Field(default="", alias="BOT_OWNER_IDS")

    # Bot behavior
    default_prefix: str = Field(default="j!", alias="DEFAULT_PREFIX")
    environment: str = Field(default="development", alias="ENVIRONMENT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    support_server_url: str = Field(
        default="https://discord.com", alias="SUPPORT_SERVER_URL"
    )
    status_rotation_seconds: int = Field(default=30, alias="STATUS_ROTATION_SECONDS")

    # Database
    database_url: str = Field(
        default=f"sqlite+aiosqlite:///{(DATABASE_DIR / 'jarvis.db').as_posix()}",
        alias="DATABASE_URL",
    )
    db_pool_size: int = Field(default=10, alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(default=20, alias="DB_MAX_OVERFLOW")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    # Lavalink v4
    lavalink_uri: str = Field(default="http://127.0.0.1:2333", alias="LAVALINK_URI")
    lavalink_password: str = Field(default="youshallnotpass", alias="LAVALINK_PASSWORD")
    lavalink_node_id: str = Field(default="jarvis-primary", alias="LAVALINK_NODE_ID")

    # FastAPI Dashboard
    dashboard_host: str = Field(default="0.0.0.0", alias="DASHBOARD_HOST")
    dashboard_port: int = Field(default=8080, alias="DASHBOARD_PORT")
    dashboard_base_url: str = Field(
        default="http://localhost:8080", alias="DASHBOARD_BASE_URL"
    )
    discord_redirect_uri: str = Field(
        default="http://localhost:8080/auth/callback", alias="DISCORD_REDIRECT_URI"
    )
    session_secret: str = Field(default="change-me-in-production", alias="SESSION_SECRET")
    csrf_secret: str = Field(default="change-csrf-in-production", alias="CSRF_SECRET")

    @field_validator("default_prefix")
    @classmethod
    def validate_prefix(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned or len(cleaned) > 10:
            raise ValueError("DEFAULT_PREFIX must be between 1 and 10 characters.")
        return cleaned

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, value: str) -> str:
        upper = value.strip().upper()
        allowed = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        return upper if upper in allowed else "INFO"

    @property
    def owner_ids(self) -> set[int]:
        """Parse comma-separated BOT_OWNER_IDS into a set of integers."""
        ids: set[int] = set()
        for part in self.bot_owner_ids_raw.split(","):
            stripped = part.strip()
            if stripped.isdigit():
                ids.add(int(stripped))
        return ids

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached validated Settings instance."""
    return Settings()


def validate_bot_startup_env(settings: Settings | None = None) -> None:
    """Ensure required bot runtime credentials are configured before connecting."""
    cfg = settings or get_settings()
    token = cfg.discord_token.strip()
    if not token or token == "YOUR_DISCORD_BOT_TOKEN":
        raise RuntimeError(
            "DISCORD_TOKEN is not configured. Copy .env.example to .env and set DISCORD_TOKEN."
        )
    if cfg.is_production and (
        cfg.session_secret == "change-me-in-production"
        or cfg.csrf_secret == "change-csrf-in-production"
    ):
        raise RuntimeError(
            "SESSION_SECRET and CSRF_SECRET must be replaced in production mode."
        )
