"""
Structured logging event catalog.

Business modules must use LoggingEvents instead of calling
logger methods directly.

Each event uses:
- a stable event name as the log message;
- structured metadata through logging's ``extra`` argument.
"""

from __future__ import annotations

from logging import Logger
from typing import Any

from app.logging.location_log_policy import (
    LocationLogPolicy,
)
from app.logging.sensitive_data import (
    SensitiveDataSanitizer,
)


class LoggingEvents:
    """Catalog of standardized structured logging events."""

    @staticmethod
    def _extra(
        event: str,
        **fields: Any,
    ) -> dict[str, Any]:
        """Build sanitized structured metadata."""

        raw_fields = {
            "event": event,
            **{key: value for key, value in fields.items() if value is not None},
        }

        return SensitiveDataSanitizer.sanitize_mapping(
            raw_fields,
        )

    @staticmethod
    def calculation_started(
        logger: Logger,
        *,
        origin: str,
        destination: str,
    ) -> None:
        """Log the start of a route calculation."""

        event = "CALCULATION_STARTED"

        location_fields = LocationLogPolicy.build(
            origin=origin,
            destination=destination,
        )

        logger.info(
            event,
            extra=LoggingEvents._extra(
                event,
                **location_fields,
            ),
        )

    @staticmethod
    def calculation_completed(
        logger: Logger,
        *,
        provider: str,
        route_count: int,
    ) -> None:
        """Log the successful completion of a route calculation."""

        event = "CALCULATION_COMPLETED"

        logger.info(
            event,
            extra=LoggingEvents._extra(
                event,
                provider=provider,
                route_count=route_count,
            ),
        )

    @staticmethod
    def calculation_failed(
        logger: Logger,
        *,
        provider: str,
        error_code: str,
        error_message: str,
        exception: Exception | None = None,
        exception_is_active: bool = False,
    ) -> None:
        """
        Log a failed route calculation.

        Active exceptions use logger.exception() so Python captures the
        currently handled traceback.

        Preserved exceptions returned by a provider use logger.error()
        with exc_info=exception.
        """

        event = "CALCULATION_FAILED"

        extra = LoggingEvents._extra(
            event,
            provider=provider,
            error_code=error_code,
            error_message=error_message,
            exception_type=(
                type(exception).__name__ if exception is not None else None
            ),
        )

        if exception_is_active:
            logger.exception(
                event,
                extra=extra,
            )
            return

        if exception is not None:
            logger.error(
                event,
                extra=extra,
                exc_info=exception,
            )
            return

        logger.error(
            event,
            extra=extra,
        )

    @staticmethod
    def provider_selected(
        logger: Logger,
        *,
        provider: str,
    ) -> None:
        """Log the provider selected for calculation."""

        event = "PROVIDER_SELECTED"

        logger.info(
            event,
            extra=LoggingEvents._extra(
                event,
                provider=provider,
            ),
        )

    @staticmethod
    def engine_started(
        logger: Logger,
    ) -> None:
        """Log the start of an engine operation."""

        event = "ENGINE_STARTED"

        logger.info(
            event,
            extra=LoggingEvents._extra(
                event,
            ),
        )

    @staticmethod
    def engine_completed(
        logger: Logger,
    ) -> None:
        """Log the successful completion of an engine operation."""

        event = "ENGINE_COMPLETED"

        logger.info(
            event,
            extra=LoggingEvents._extra(
                event,
            ),
        )

    @staticmethod
    def parser_started(
        logger: Logger,
    ) -> None:
        """Log the start of a parser operation."""

        event = "PARSER_STARTED"

        logger.info(
            event,
            extra=LoggingEvents._extra(
                event,
            ),
        )

    @staticmethod
    def parser_completed(
        logger: Logger,
        *,
        route_count: int,
    ) -> None:
        """Log the successful completion of a parser operation."""

        event = "PARSER_COMPLETED"

        logger.info(
            event,
            extra=LoggingEvents._extra(
                event,
                route_count=route_count,
            ),
        )
