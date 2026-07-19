"""
Application logging utilities.

This module provides a centralized logging configuration for the
DistanceCalculatorPro project.

Usage:

    from app.utils.logger import get_logger

    logger = get_logger(__name__)

    logger.info("Application started.")
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.config import (
    APP_MODE,
    AppMode,
    LOG_FILE,
    LOG_LEVEL,
)


def _create_formatter() -> logging.Formatter:
    """Create the default log formatter."""

    return logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _configure_root_logger() -> None:
    """Configure the application root logger."""

    root_logger = logging.getLogger()

    # Already configured
    if root_logger.handlers:
        return

    log_path = Path(LOG_FILE)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    formatter = _create_formatter()

    root_logger.setLevel(LOG_LEVEL)

    # File handler
    file_handler = logging.FileHandler(
        filename=log_path,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)

    # Console handler (development only)
    if APP_MODE is AppMode.DEVELOPMENT:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)


def get_logger(name: str) -> logging.Logger:
    """
    Return an application logger.

    Parameters
    ----------
    name:
        Usually __name__.

    Returns
    -------
    logging.Logger
    """

    _configure_root_logger()

    return logging.getLogger(name)