"""
Logging manager.

Provides centralized logger configuration for the application.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.logging.formatter import StructuredJsonFormatter

from .config import (
    LOG_DIRECTORY,
    LOG_FILENAME,
    LOG_LEVEL,
    LOGGER_NAME,
)


class LoggingManager:
    """Centralized logging manager."""

    _initialized = False
    _root_logger: logging.Logger | None = None

    @classmethod
    def _initialize(cls) -> None:
        """Initialize the logging system once."""

        if cls._initialized:
            return

        log_directory = Path(LOG_DIRECTORY)
        log_directory.mkdir(parents=True, exist_ok=True)

        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(getattr(logging, LOG_LEVEL.upper()))
        logger.propagate = False

        if not logger.handlers:
            formatter = StructuredJsonFormatter()

            # Console Handler
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

            # File Handler
            file_handler = logging.FileHandler(
                log_directory / LOG_FILENAME,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        cls._root_logger = logger
        cls._initialized = True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """
        Return a module logger.

        Parameters
        ----------
        name:
            Module name, typically __name__.

        Returns
        -------
        logging.Logger
        """

        cls._initialize()

        return cls._root_logger.getChild(name)