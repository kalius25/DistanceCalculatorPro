from __future__ import annotations

import json
import logging

from app.logging.formatter import StructuredJsonFormatter


def make_record(
    *,
    message: str = "TEST_EVENT",
    level: int = logging.INFO,
    extra: dict | None = None,
    exc_info=None,
    stack_info: str | None = None,
) -> logging.LogRecord:
    record = logging.LogRecord(
        name="DistanceCalculatorPro.test",
        level=level,
        pathname=__file__,
        lineno=10,
        msg=message,
        args=(),
        exc_info=exc_info,
    )

    record.created = 0

    if extra:
        for key, value in extra.items():
            setattr(
                record,
                key,
                value,
            )

    record.stack_info = stack_info

    return record


def test_format_structured_record():
    formatter = StructuredJsonFormatter()

    record = make_record(
        message="CALCULATION_COMPLETED",
        extra={
            "event": "CALCULATION_COMPLETED",
            "provider": "google_web",
            "route_count": 3,
        },
    )

    payload = json.loads(
        formatter.format(record),
    )

    assert payload == {
        "timestamp": "1970-01-01T00:00:00.000Z",
        "level": "INFO",
        "logger": "DistanceCalculatorPro.test",
        "event": "CALCULATION_COMPLETED",
        "message": "CALCULATION_COMPLETED",
        "provider": "google_web",
        "route_count": 3,
    }


def test_format_uses_message_as_event_fallback():
    formatter = StructuredJsonFormatter()

    record = make_record(
        message="APPLICATION_STARTED",
    )

    payload = json.loads(
        formatter.format(record),
    )

    assert payload["event"] == "APPLICATION_STARTED"
    assert payload["message"] == "APPLICATION_STARTED"


def test_format_includes_exception():
    formatter = StructuredJsonFormatter()

    try:
        raise RuntimeError(
            "Engine failed.",
        )
    except RuntimeError:
        import sys

        exc_info = sys.exc_info()

    record = make_record(
        message="CALCULATION_FAILED",
        level=logging.ERROR,
        extra={
            "event": "CALCULATION_FAILED",
            "error_code": "ENGINE_ERROR",
        },
        exc_info=exc_info,
    )

    payload = json.loads(
        formatter.format(record),
    )

    assert payload["level"] == "ERROR"
    assert payload["error_code"] == "ENGINE_ERROR"
    assert "RuntimeError: Engine failed." in (
        payload["exception"]
    )


def test_format_includes_existing_exception_text():
    formatter = StructuredJsonFormatter()

    record = make_record(
        message="CALCULATION_FAILED",
        level=logging.ERROR,
    )
    record.exc_text = "Stored exception text"

    payload = json.loads(
        formatter.format(record),
    )

    assert payload["exception"] == (
        "Stored exception text"
    )


def test_format_includes_stack_info():
    formatter = StructuredJsonFormatter()

    record = make_record(
        stack_info="Stack information",
    )

    payload = json.loads(
        formatter.format(record),
    )

    assert payload["stack_info"] == (
        "Stack information"
    )


def test_json_default_converts_unsupported_value():
    formatter = StructuredJsonFormatter()

    class CustomValue:
        def __str__(self) -> str:
            return "custom-value"

    record = make_record(
        extra={
            "custom": CustomValue(),
        },
    )

    payload = json.loads(
        formatter.format(record),
    )

    assert payload["custom"] == "custom-value"


def test_extract_extra_ignores_private_fields():
    record = make_record(
        extra={
            "event": "TEST_EVENT",
            "provider": "google_web",
            "_private": "hidden",
        },
    )

    result = (
        StructuredJsonFormatter
        ._extract_extra_fields(record)
    )

    assert result == {
        "provider": "google_web",
    }

def test_formatter_redacts_sensitive_extra_fields():
    formatter = StructuredJsonFormatter()

    record = make_record(
        message="SECURITY_TEST",
        extra={
            "event": "SECURITY_TEST",
            "password": "123456",
            "email": "user@example.com",
        },
    )

    payload = json.loads(
        formatter.format(record),
    )

    assert payload["password"] == "[REDACTED]"
    assert payload["email"] == "u***@example.com"

def test_json_default_converts_unknown_object():
    class CustomValue:
        def __str__(self) -> str:
            return "custom-value"

    assert (
        StructuredJsonFormatter._json_default(
            CustomValue(),
        )
        == "custom-value"
    )
