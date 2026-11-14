"""
JARVIS — Structured Logging System
Developer: Shadow
"""

from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

import structlog

from config import BOT_NAME, LOGS_DIR


def setup_logging(log_level: str = "INFO", log_dir: Path = LOGS_DIR) -> logging.Logger:
    """Configure console + rotating file structured logging for JARVIS."""
    log_dir.mkdir(parents=True, exist_ok=True)
    level = getattr(logging, log_level.upper(), logging.INFO)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.handlers.clear()

    # UTF-8 safe console handler (supports Windows & Linux Mint)
    console_stream = open(sys.stdout.fileno(), mode="w", encoding="utf-8", buffering=1, closefd=False)
    console_handler = logging.StreamHandler(console_stream)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Rotating file handler (5 MB x 5 files)
    file_handler = RotatingFileHandler(
        filename=log_dir / "jarvis.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    # Quiet noisy third-party loggers slightly
    logging.getLogger("discord.http").setLevel(logging.WARNING)
    logging.getLogger("discord.gateway").setLevel(logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    jarvis_logger = logging.getLogger(BOT_NAME)
    jarvis_logger.info("Structured logging initialized at level %s", log_level)
    return jarvis_logger
