"""Logging configuration for CLI Task Manager.

Provides structured logging with rotating file handlers and clear console formatting.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional

import config


def setup_logger(
    name: str = "TaskManager",
    log_level: int = logging.INFO,
    log_file: Optional[Path] = None,
) -> logging.Logger:
    """Configure and return a structured logger instance."""
    logger = logging.getLogger(name)

    # Avoid duplicate handlers if already configured
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)  # Capture all, handlers will filter
    formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)-7s] [%(name)s]: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console Handler (respects log_level parameter)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (with rotation: 2MB max, up to 3 backups)
    target_file = log_file or config.LOG_FILE
    target_file.parent.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        filename=str(target_file),
        maxBytes=2 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)  # Keep verbose logs in file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
