"""
JSON formatter for structured application logs.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from typing import Any

from app.logging.sensitive_data import (
    SensitiveDataSanitizer,
)

_STANDARD_LOG_RECORD_FIELDS = frozenset(
    {
        "args",
        "asctime",
        "created",
        "exc_info",
        "exc_text",
        "filename",
        "funcName",
        "levelname",
        "levelno",
        "lineno",
        "module",
        "msecs",
        "message",
        "msg",
        "name",
        "pathname",
        "process",
        "processName",
        "relativeCreated",
        "stack_info",
        "thread",
        "threadName",
        "taskName",
    }
)


class StructuredJsonFormatter(logging.Formatter):
    """Convert logging records into one-line JSON objects."""

    def format(
        self,
        record: logging.LogRecord,
    ) -> str:
        """Format a LogRecord as JSON."""

        record_message = record.getMessage()

        payload: dict[str, Any] = {
            "timestamp": self._format_timestamp(
                record.created,
            ),
            "level": record.levelname,
            "logger": record.name,
            "event": getattr(
                record,
                "event",
                record_message,
            ),
            "message": record_message,
        }

        custom_fields = self._extract_extra_fields(
            record,
        )

        payload.update(
            SensitiveDataSanitizer.sanitize_mapping(
                custom_fields,
            ),
        )

        if record.exc_info:
            payload["exception"] = (
                self.formatException(record.exc_info)
            )
        elif record.exc_text:
            payload["exception"] = record.exc_text

        if record.stack_info:
            payload["stack_info"] = (
                self.formatStack(record.stack_info)
            )

        return json.dumps(
            payload,
            ensure_ascii=False,
            default=self._json_default,
            separators=(",", ":"),
        )

    @staticmethod
    def _format_timestamp(
        created: float,
    ) -> str:
        """Return an ISO-8601 UTC timestamp."""

        return (
            datetime.fromtimestamp(
                created,
                tz=timezone.utc,
            )
            .isoformat(
                timespec="milliseconds",
            )
            .replace(
                "+00:00",
                "Z",
            )
        )

    @staticmethod
    def _extract_extra_fields(
        record: logging.LogRecord,
    ) -> dict[str, Any]:
        """Extract custom fields supplied through logging extra."""

        return {
            key: value
            for key, value in record.__dict__.items()
            if (
                key not in _STANDARD_LOG_RECORD_FIELDS
                and not key.startswith("_")
                and key not in {
                    "event",
                }
            )
        }

    @staticmethod
    def _json_default(
        value: object,
    ) -> str:
        """Serialize unsupported values safely."""

        return str(value)


__all__ = [
    "StructuredJsonFormatter",
]