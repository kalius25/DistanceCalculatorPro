from __future__ import annotations

import logging

from app.logging import LoggingManager


def test_logging_manager_reuses_existing_handler():
    application_logger = logging.getLogger(
        "DistanceCalculatorPro",
    )

    original_handlers = list(
        application_logger.handlers,
    )
    original_level = application_logger.level
    original_propagate = application_logger.propagate
    original_initialized = LoggingManager._initialized

    existing_handler = logging.NullHandler()

    try:
        application_logger.handlers.clear()
        application_logger.addHandler(
            existing_handler,
        )

        LoggingManager._initialized = False

        logger = LoggingManager.get_logger(
            "existing-handler",
        )

        assert existing_handler in application_logger.handlers
        assert application_logger.handlers.count(
            existing_handler,
        ) == 1

        assert logger.name == (
            "DistanceCalculatorPro.existing-handler"
        )

    finally:
        application_logger.handlers.clear()

        for handler in original_handlers:
            application_logger.addHandler(
                handler,
            )

        application_logger.setLevel(
            original_level,
        )
        application_logger.propagate = original_propagate

        LoggingManager._initialized = original_initialized