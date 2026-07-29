"""
Logging event catalog.

Provides standardized application events for logging.

Business modules must use LoggingEvents instead of calling
logger.info(), logger.debug(), logger.warning(), logger.error(),
or logger.exception() directly.
"""

from __future__ import annotations

from logging import Logger


class LoggingEvents:
    """Catalog of standardized application logging events."""

    @staticmethod
    def calculation_started(
        logger: Logger,
        *,
        origin: str,
        destination: str,
    ) -> None:
        """Log the start of a route calculation."""

        logger.info(
            "CALCULATION_STARTED | origin=%s | destination=%s",
            origin,
            destination,
        )

    @staticmethod
    def calculation_completed(
        logger: Logger,
        *,
        provider: str,
        route_count: int,
    ) -> None:
        """Log the successful completion of a route calculation."""

        logger.info(
            "CALCULATION_COMPLETED | provider=%s | routes=%d",
            provider,
            route_count,
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

        Parameters
        ----------
        logger:
            Logger owned by the calling module.

        provider:
            Provider involved in the calculation.

        error_code:
            Stable application error code.

        error_message:
            Human-readable error description.

        exception:
            Original exception when available.

        exception_is_active:
            True when this method is called from inside the active
            exception handler. In that case logger.exception() is used.
        """

        message = (
            "CALCULATION_FAILED"
            " | provider=%s"
            " | error_code=%s"
            " | error=%s"
        )

        arguments = (
            provider,
            error_code,
            error_message,
        )

        if exception_is_active:
            logger.exception(
                message,
                *arguments,
            )
            return

        if exception is not None:
            logger.error(
                message,
                *arguments,
                exc_info=exception,
            )
            return

        logger.error(
            message,
            *arguments,
        )

    @staticmethod
    def provider_selected(
        logger: Logger,
        *,
        provider: str,
    ) -> None:
        """Log the provider selected for calculation."""

        logger.info(
            "PROVIDER_SELECTED | provider=%s",
            provider,
        )

    @staticmethod
    def engine_started(
        logger: Logger,
    ) -> None:
        """Log the start of an engine operation."""

        logger.info(
            "ENGINE_STARTED",
        )

    @staticmethod
    def engine_completed(
        logger: Logger,
    ) -> None:
        """Log the successful completion of an engine operation."""

        logger.info(
            "ENGINE_COMPLETED",
        )

    @staticmethod
    def parser_started(
        logger: Logger,
    ) -> None:
        """Log the start of a parser operation."""

        logger.info(
            "PARSER_STARTED",
        )

    @staticmethod
    def parser_completed(
        logger: Logger,
        *,
        route_count: int,
    ) -> None:
        """Log the successful completion of a parser operation."""

        logger.info(
            "PARSER_COMPLETED | routes=%d",
            route_count,
        )