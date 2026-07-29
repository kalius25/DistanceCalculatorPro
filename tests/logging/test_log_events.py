from __future__ import annotations

from unittest.mock import Mock

from app.logging import LoggingEvents


def test_calculation_started(
    monkeypatch,
):
    logger = Mock()

    location_fields = {
        "origin_hash": "origin-hash",
        "destination_hash": "destination-hash",
    }

    monkeypatch.setattr(
        (
            "app.logging.log_events."
            "LocationLogPolicy.build"
        ),
        lambda **kwargs: location_fields,
    )

    LoggingEvents.calculation_started(
        logger,
        origin="Can Tho",
        destination="Ho Chi Minh City",
    )

    logger.info.assert_called_once_with(
        "CALCULATION_STARTED",
        extra={
            "event": "CALCULATION_STARTED",
            "origin_hash": "origin-hash",
            "destination_hash": (
                "destination-hash"
            ),
        },
    )


def test_calculation_completed():
    logger = Mock()

    LoggingEvents.calculation_completed(
        logger,
        provider="google_web",
        route_count=3,
    )

    logger.info.assert_called_once_with(
        "CALCULATION_COMPLETED",
        extra={
            "event": "CALCULATION_COMPLETED",
            "provider": "google_web",
            "route_count": 3,
        },
    )


def test_calculation_failed_uses_active_exception():
    logger = Mock()
    exception = ValueError(
        "Origin is empty.",
    )

    LoggingEvents.calculation_failed(
        logger,
        provider="GoogleWebProvider",
        error_code="VALIDATION_ERROR",
        error_message="Origin is empty.",
        exception=exception,
        exception_is_active=True,
    )

    logger.exception.assert_called_once_with(
        "CALCULATION_FAILED",
        extra={
            "event": "CALCULATION_FAILED",
            "provider": "GoogleWebProvider",
            "error_code": "VALIDATION_ERROR",
            "error_message": "Origin is empty.",
            "exception_type": "ValueError",
        },
    )

    logger.error.assert_not_called()


def test_calculation_failed_logs_preserved_exception():
    logger = Mock()
    exception = RuntimeError(
        "Engine failed.",
    )

    LoggingEvents.calculation_failed(
        logger,
        provider="google_web",
        error_code="ENGINE_ERROR",
        error_message="Engine failed.",
        exception=exception,
    )

    logger.error.assert_called_once_with(
        "CALCULATION_FAILED",
        extra={
            "event": "CALCULATION_FAILED",
            "provider": "google_web",
            "error_code": "ENGINE_ERROR",
            "error_message": "Engine failed.",
            "exception_type": "RuntimeError",
        },
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
        "CALCULATION_FAILED",
        extra={
            "event": "CALCULATION_FAILED",
            "provider": "google_web",
            "error_code": "UNKNOWN_ERROR",
            "error_message": "Unknown error.",
        },
    )

    logger.exception.assert_not_called()


def test_provider_selected():
    logger = Mock()

    LoggingEvents.provider_selected(
        logger,
        provider="GoogleWebProvider",
    )

    logger.info.assert_called_once_with(
        "PROVIDER_SELECTED",
        extra={
            "event": "PROVIDER_SELECTED",
            "provider": "GoogleWebProvider",
        },
    )


def test_engine_started():
    logger = Mock()

    LoggingEvents.engine_started(logger)

    logger.info.assert_called_once_with(
        "ENGINE_STARTED",
        extra={
            "event": "ENGINE_STARTED",
        },
    )


def test_engine_completed():
    logger = Mock()

    LoggingEvents.engine_completed(logger)

    logger.info.assert_called_once_with(
        "ENGINE_COMPLETED",
        extra={
            "event": "ENGINE_COMPLETED",
        },
    )


def test_parser_started():
    logger = Mock()

    LoggingEvents.parser_started(logger)

    logger.info.assert_called_once_with(
        "PARSER_STARTED",
        extra={
            "event": "PARSER_STARTED",
        },
    )


def test_parser_completed():
    logger = Mock()

    LoggingEvents.parser_completed(
        logger,
        route_count=3,
    )

    logger.info.assert_called_once_with(
        "PARSER_COMPLETED",
        extra={
            "event": "PARSER_COMPLETED",
            "route_count": 3,
        },
    )

def test_extra_omits_none_values():
    result = LoggingEvents._extra(
        "TEST_EVENT",
        provider="google_web",
        error_code=None,
    )

    assert result == {
        "event": "TEST_EVENT",
        "provider": "google_web",
    }

