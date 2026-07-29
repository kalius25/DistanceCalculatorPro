from __future__ import annotations

from enum import Enum
from unittest.mock import Mock

from app.logging import LoggingEvents
from app.services.calculation_service import CalculationService


def test_calculation_failed_uses_logger_exception_for_active_exception():
    logger = Mock()

    LoggingEvents.calculation_failed(
        logger,
        provider="GoogleWebProvider",
        error_code="VALIDATION_ERROR",
        error_message="Origin is empty.",
        exception=ValueError("Origin is empty."),
        exception_is_active=True,
    )

    logger.exception.assert_called_once_with(
        (
            "CALCULATION_FAILED"
            " | provider=%s"
            " | error_code=%s"
            " | error=%s"
        ),
        "GoogleWebProvider",
        "VALIDATION_ERROR",
        "Origin is empty.",
    )

    logger.error.assert_not_called()


def test_calculation_failed_logs_preserved_exception():
    logger = Mock()
    exception = RuntimeError("Engine failed.")

    LoggingEvents.calculation_failed(
        logger,
        provider="google_web",
        error_code="ENGINE_ERROR",
        error_message="Engine failed.",
        exception=exception,
    )

    logger.error.assert_called_once_with(
        (
            "CALCULATION_FAILED"
            " | provider=%s"
            " | error_code=%s"
            " | error=%s"
        ),
        "google_web",
        "ENGINE_ERROR",
        "Engine failed.",
        exc_info=exception,
    )

    logger.exception.assert_not_called()


def test_calculation_failed_without_exception():
    logger = Mock()

    LoggingEvents.calculation_failed(
        logger,
        provider="google_web",
        error_code="UNKNOWN_ERROR",
        error_message="Unknown error.",
    )

    logger.error.assert_called_once_with(
        (
            "CALCULATION_FAILED"
            " | provider=%s"
            " | error_code=%s"
            " | error=%s"
        ),
        "google_web",
        "UNKNOWN_ERROR",
        "Unknown error.",
    )

    logger.exception.assert_not_called()


class SampleErrorCode(Enum):
    ENGINE_ERROR = "ENGINE_ERROR"


def test_get_error_code_value_when_none():
    assert (
        CalculationService._get_error_code_value(None)
        == "UNKNOWN_ERROR"
    )


def test_get_error_code_value_from_enum():
    assert (
        CalculationService._get_error_code_value(
            SampleErrorCode.ENGINE_ERROR,
        )
        == "ENGINE_ERROR"
    )


def test_get_error_code_value_from_plain_string():
    assert (
        CalculationService._get_error_code_value(
            "CUSTOM_ERROR",
        )
        == "CUSTOM_ERROR"
    )

def test_engine_started():
    logger = Mock()

    LoggingEvents.engine_started(logger)

    logger.info.assert_called_once_with(
        "ENGINE_STARTED",
    )


def test_engine_completed():
    logger = Mock()

    LoggingEvents.engine_completed(logger)

    logger.info.assert_called_once_with(
        "ENGINE_COMPLETED",
    )


def test_parser_started():
    logger = Mock()

    LoggingEvents.parser_started(logger)

    logger.info.assert_called_once_with(
        "PARSER_STARTED",
    )


def test_parser_completed():
    logger = Mock()

    LoggingEvents.parser_completed(
        logger,
        route_count=3,
    )

    logger.info.assert_called_once_with(
        "PARSER_COMPLETED | routes=%d",
        3,
    )
