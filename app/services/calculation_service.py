"""
Business service for route calculation.
"""

from __future__ import annotations

from app.exceptions import (
    DistanceCalculatorError,
    ValidationException,
)
from app.logging import (
    LoggingEvents,
    LoggingManager,
)
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider

logger = LoggingManager.get_logger(__name__)


class CalculationService:
    """
    Coordinate route calculation and select the best route.

    The service receives its route provider through constructor
    injection. It does not create, select, or configure providers.
    """

    def __init__(
        self,
        provider: BaseProvider,
    ) -> None:
        """
        Initialize the calculation service.

        Parameters
        ----------
        provider:
            Provider used to perform route calculations.
        """
        self._provider = provider

    @property
    def provider(self) -> BaseProvider:
        """
        Return the injected route provider.

        This property preserves one-level compatibility for existing
        callers while keeping the dependency internally private.
        """
        return self._provider

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:
        """
        Calculate routes for the supplied request.

        Processing sequence:
        1. Validate the request.
        2. Log calculation start.
        3. Invoke the injected provider.
        4. Process provider failure or success.
        5. Select the best route when routes are available.

        Unexpected exceptions are intentionally allowed to propagate.
        """
        provider_name = self._get_provider_name()

        try:
            self._validate(request)

            LoggingEvents.calculation_started(
                logger,
                origin=request.origin,
                destination=request.destination,
            )

            LoggingEvents.provider_selected(
                logger,
                provider=provider_name,
            )

            result = self._provider.calculate(request)

            if not result.success:
                return self._handle_failed_result(
                    result=result,
                    provider_name=provider_name,
                )

            return self._handle_successful_result(
                result=result,
                provider_name=provider_name,
            )

        except DistanceCalculatorError as exc:
            return self._handle_domain_exception(
                request=request,
                exception=exc,
                provider_name=provider_name,
            )

    def _get_provider_name(self) -> str:
        """Return the injected provider class name."""
        return self._provider.__class__.__name__

    @staticmethod
    def _handle_failed_result(
        *,
        result: RouteResult,
        provider_name: str,
    ) -> RouteResult:
        """
        Log and return a failed provider result unchanged.
        """
        LoggingEvents.calculation_failed(
            logger,
            provider=result.provider or provider_name,
            error_code=CalculationService._get_error_code_value(
                result.error_code,
            ),
            error_message=result.error or "Unknown error.",
            exception=result.exception,
        )

        return result

    @staticmethod
    def _handle_successful_result(
        *,
        result: RouteResult,
        provider_name: str,
    ) -> RouteResult:
        """
        Select the best route and log successful completion.
        """
        if result.routes:
            result.selected_route = (
                CalculationService._select_best_route(
                    result,
                )
            )

        LoggingEvents.calculation_completed(
            logger,
            provider=result.provider or provider_name,
            route_count=len(result.routes),
        )

        return result

    @staticmethod
    def _handle_domain_exception(
        *,
        request: RouteRequest,
        exception: DistanceCalculatorError,
        provider_name: str,
    ) -> RouteResult:
        """
        Convert an application-domain exception into RouteResult.
        """
        LoggingEvents.calculation_failed(
            logger,
            provider=provider_name,
            error_code=CalculationService._get_error_code_value(
                exception.error_code,
            ),
            error_message=str(exception),
            exception=exception,
            exception_is_active=True,
        )

        return RouteResult(
            success=False,
            request=request,
            provider=provider_name,
            error=str(exception),
            error_code=exception.error_code,
            context=exception.context,
            exception=exception,
        )

    @staticmethod
    def _get_error_code_value(
        error_code: object | None,
    ) -> str:
        """
        Convert an error code to a stable logging value.

        Enum-based error codes and plain strings are supported without
        coupling the service to a concrete ErrorCode implementation.
        """
        if error_code is None:
            return "UNKNOWN_ERROR"

        value = getattr(
            error_code,
            "value",
            None,
        )

        if value is not None:
            return str(value)

        return str(error_code)

    @staticmethod
    def _validate(
        request: RouteRequest,
    ) -> None:
        """
        Validate a route calculation request.
        """
        origin = request.origin.strip()
        destination = request.destination.strip()

        if not origin:
            raise ValidationException(
                "Origin is empty.",
                context={
                    "field": "origin",
                },
            )

        if not destination:
            raise ValidationException(
                "Destination is empty.",
                context={
                    "field": "destination",
                },
            )

        if origin == destination:
            raise ValidationException(
                "Origin and destination cannot be the same.",
                context={
                    "origin": request.origin,
                    "destination": request.destination,
                },
            )

    @staticmethod
    def _select_best_route(
        result: RouteResult,
    ) -> int:
        """
        Select the best route index.

        Selection priority:
        1. Shortest duration.
        2. Shortest distance.
        """
        return min(
            range(len(result.routes)),
            key=lambda index: (
                result.routes[index].duration_minutes,
                result.routes[index].distance_km,
            ),
        )


__all__ = [
    "CalculationService",
]