"""
JARVIS — Automatic Modular Cog & Extension Loader
Developer: Shadow
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

from discord.ext import commands

from config import BASE_DIR

logger = logging.getLogger("JARVIS.Loader")


@dataclass
class LoadReport:
    """Summary of cog extension loading across JARVIS modules."""

    loaded: list[str] = field(default_factory=list)
    failed: dict[str, str] = field(default_factory=dict)
    skipped: list[str] = field(default_factory=list)


def discover_extensions(cogs_dir: Path | None = None) -> list[str]:
    """
    Discover Python Cog modules under cogs/<category>/<module>.py.
    Skips __init__.py and private modules prefixed with '_'.
    """
    root = cogs_dir or (BASE_DIR / "cogs")
    if not root.exists():
        return []

    extensions: list[str] = []
    for category_dir in sorted(root.iterdir()):
        if not category_dir.is_dir() or category_dir.name.startswith("_"):
            continue
        for py_file in sorted(category_dir.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            # Only load files that declare an async setup(bot) entrypoint
            source = py_file.read_text(encoding="utf-8", errors="ignore")
            if "def setup(" not in source:
                continue
            extensions.append(f"cogs.{category_dir.name}.{py_file.stem}")
    return extensions


async def load_all_extensions(bot: commands.Bot) -> LoadReport:
    """Safely load all discovered Cog extensions with failure isolation."""
    report = LoadReport()
    for ext in discover_extensions():
        if ext in bot.extensions:
            report.skipped.append(ext)
            continue
        try:
            await bot.load_extension(ext)
            report.loaded.append(ext)
            logger.info("Loaded extension: %s", ext)
        except Exception as exc:
            report.failed[ext] = f"{type(exc).__name__}: {exc}"
            logger.exception("Failed to load extension %s: %s", ext, exc)
    return report
