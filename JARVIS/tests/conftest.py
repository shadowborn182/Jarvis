"""
JARVIS — Pytest Fixtures
Developer: Shadow
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest_asyncio

# Ensure JARVIS root is importable
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from config import Settings
from core.database import DatabaseManager


@pytest_asyncio.fixture
async def db_manager(tmp_path: Path) -> DatabaseManager:
    db_file = tmp_path / "test_jarvis.db"
    settings = Settings(
        DISCORD_TOKEN="test_token",
        DATABASE_URL=f"sqlite+aiosqlite:///{db_file.as_posix()}",
        DEFAULT_PREFIX="j!",
    )
    manager = DatabaseManager(settings)
    await manager.init_models()
    yield manager
    await manager.close()
