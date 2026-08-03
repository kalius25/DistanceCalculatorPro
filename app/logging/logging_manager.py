"""
Logging manager.

Provides centralized logger configuration for the application.
"""

from __future__ import annotations

import logging
from pathlib import Path

from app.configuration.models import LoggingConfig
from app.logging.formatter import StructuredJsonFormatter

from .config import (
    LOG_DIRECTORY,
    LOG_FILENAME,
    LOG_LEVEL,
    LOGGER_NAME,
)


class LoggingManager:
    """
    Centralized logging manager.

    Configuration should be supplied once by the application composition root:

        LoggingManager.configure(app_config.logging)

    Business modules must only request loggers through get_logger().
    """

    _MANAGED_HANDLER_ATTRIBUTE = "_distance_calculator_managed"

    _initialized = False
    _root_logger: logging.Logger | None = None
    _config: LoggingConfig | None = None

    @classmethod
    def configure(
        cls,
        config: LoggingConfig,
    ) -> None:
        """
        Supply logging configuration to the manager.

        Parameters
        ----------
        config:
            Immutable logging configuration.

        Notes
        -----
        Supplying a different configuration resets the logging manager.
        Supplying an equal configuration does not recreate handlers.
        """

        if cls._config == config:
            return

        cls._close_managed_handlers()
        cls._config = config
        cls._root_logger = None
        cls._initialized = False

    @classmethod
    def set_debug_enabled(cls, enabled: bool) -> None:
        """Switch the managed application logger between DEBUG and config level."""
        logger = cls._initialize()
        if enabled:
            logger.setLevel(logging.DEBUG)
            for handler in logger.handlers:
                if getattr(handler, cls._MANAGED_HANDLER_ATTRIBUTE, False):
                    handler.setLevel(logging.DEBUG)
            return

        config = cls._get_effective_config()
        level = getattr(logging, config.level.upper())
        logger.setLevel(level)
        for handler in logger.handlers:
            if getattr(handler, cls._MANAGED_HANDLER_ATTRIBUTE, False):
                handler.setLevel(level)

    @classmethod
    def _get_effective_config(cls) -> LoggingConfig:
        """
        Return the active logging configuration.

        The fallback configuration preserves compatibility during EX-007.4.
        It will be removed after the composition root and all dependent
        modules have been refactored.
        """

        if cls._config is not None:
            return cls._config

        return LoggingConfig(
            level=LOG_LEVEL,
            directory=str(LOG_DIRECTORY),
            filename=LOG_FILENAME,
        )

    @classmethod
    def _initialize(cls) -> logging.Logger:
        if cls._initialized and cls._root_logger is not None:
            return cls._root_logger

        config = cls._get_effective_config()

        log_directory = Path(config.directory)
        log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        logger = logging.getLogger(LOGGER_NAME)
        logger.setLevel(
            getattr(
                logging,
                config.level.upper(),
            )
        )
        logger.propagate = False

        managed_handlers = [
            handler
            for handler in logger.handlers
            if getattr(
                handler,
                cls._MANAGED_HANDLER_ATTRIBUTE,
                False,
            )
        ]

        if not managed_handlers:
            formatter = StructuredJsonFormatter()

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            setattr(
                console_handler,
                cls._MANAGED_HANDLER_ATTRIBUTE,
                True,
            )
            logger.addHandler(console_handler)

            file_handler = logging.FileHandler(
                log_directory / config.filename,
                encoding="utf-8",
            )
            file_handler.setFormatter(formatter)
            setattr(
                file_handler,
                cls._MANAGED_HANDLER_ATTRIBUTE,
                True,
            )
            logger.addHandler(file_handler)

        cls._root_logger = logger
        cls._initialized = True

        return logger

    @classmethod
    def get_logger(
        cls,
        name: str,
    ) -> logging.Logger:
        root_logger = cls._initialize()

        return root_logger.getChild(name)

    @classmethod
    def _close_managed_handlers(cls) -> None:
        """
        Remove and close handlers owned by LoggingManager.

        External handlers such as pytest log capture handlers must remain intact.
        """

        logger = logging.getLogger(LOGGER_NAME)

        managed_handlers = [
            handler
            for handler in logger.handlers
            if getattr(
                handler,
                cls._MANAGED_HANDLER_ATTRIBUTE,
                False,
            )
        ]

        for handler in managed_handlers:
            logger.removeHandler(handler)
            handler.close()

    @classmethod
    def reset(cls) -> None:
        """
        Reset logging state.

        Intended for application shutdown and unit-test isolation.
        Business modules must not call this method.
        """

        cls._close_managed_handlers()
        cls._config = None
        cls._root_logger = None
        cls._initialized = False
