"""
JARVIS — Async SQLAlchemy Database Manager
Supports SQLite (local dev) and PostgreSQL (production) with pooling, health checks & backups.
Developer: Shadow
"""

from __future__ import annotations

import logging
import shutil
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import AsyncIterator

from sqlalchemy import event, select, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import DATABASE_DIR, Settings, get_settings
from database.models import Base, GuildSettings, SecuritySettings

logger = logging.getLogger("JARVIS.Database")


class DatabaseManager:
    """Manages async SQLAlchemy connections, sessions, initialization, and backups."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.engine: AsyncEngine = self._create_engine()
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    def _create_engine(self) -> AsyncEngine:
        url = self.settings.database_url
        if self.settings.is_sqlite:
            engine = create_async_engine(
                url,
                echo=self.settings.db_echo,
                future=True,
                connect_args={"check_same_thread": False},
            )

            @event.listens_for(engine.sync_engine, "connect")
            def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA foreign_keys=ON;")
                cursor.execute("PRAGMA synchronous=NORMAL;")
                cursor.close()

            return engine

        return create_async_engine(
            url,
            echo=self.settings.db_echo,
            future=True,
            pool_size=self.settings.db_pool_size,
            max_overflow=self.settings.db_max_overflow,
            pool_pre_ping=True,
            pool_recycle=1800,
        )

    async def init_models(self) -> None:
        """Create tables if they do not exist (Alembic recommended in production)."""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables verified (%s).", "SQLite" if self.settings.is_sqlite else "PostgreSQL")

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Provide an async transactional session with automatic rollback on failure."""
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise

    async def health_check(self) -> bool:
        """Execute a lightweight query to verify database responsiveness."""
        try:
            async with self.engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception as exc:
            logger.exception("Database health check failed: %s", exc)
            return False

    async def ensure_guild(self, guild_id: int) -> GuildSettings:
        """Fetch or atomically provision GuildSettings + default SecuritySettings."""
        async with self.session() as session:
            result = await session.execute(
                select(GuildSettings).where(GuildSettings.guild_id == guild_id)
            )
            guild = result.scalar_one_or_none()
            if guild is None:
                guild = GuildSettings(
                    guild_id=guild_id,
                    prefix=self.settings.default_prefix,
                )
                session.add(guild)
                await session.flush()
                session.add(SecuritySettings(guild_id=guild_id))
            return guild

    async def get_guild_prefix(self, guild_id: int) -> str:
        """Return persisted prefix for a guild, falling back to DEFAULT_PREFIX."""
        async with self.session_factory() as session:
            result = await session.execute(
                select(GuildSettings.prefix).where(GuildSettings.guild_id == guild_id)
            )
            prefix = result.scalar_one_or_none()
            return prefix or self.settings.default_prefix

    async def set_guild_prefix(self, guild_id: int, new_prefix: str) -> str:
        """Persist a new guild prefix and return it."""
        async with self.session() as session:
            result = await session.execute(
                select(GuildSettings).where(GuildSettings.guild_id == guild_id)
            )
            guild = result.scalar_one_or_none()
            if guild is None:
                guild = GuildSettings(guild_id=guild_id, prefix=new_prefix)
                session.add(guild)
            else:
                guild.prefix = new_prefix
            return new_prefix

    def backup_sqlite(self) -> Path | None:
        """Create a timestamped local SQLite backup if running on SQLite."""
        if not self.settings.is_sqlite:
            return None
        db_path = DATABASE_DIR / "jarvis.db"
        if not db_path.exists():
            return None
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        backup_path = DATABASE_DIR / "backups" / f"jarvis_backup_{timestamp}.db"
        shutil.copy2(db_path, backup_path)
        logger.info("Created SQLite backup at %s", backup_path)
        return backup_path

    async def close(self) -> None:
        """Dispose database engine connections cleanly on shutdown."""
        await self.engine.dispose()
        logger.info("Database engine disposed.")
