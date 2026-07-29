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
    """Coordinate route calculation and select the best route."""

    def __init__(
        self,
        provider: BaseProvider,
    ) -> None:
        self.provider = provider

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:
        """
        Calculate routes for the supplied request.

        The service validates the request, invokes the configured
        provider and selects the best available route.
        """

        provider_name = self.provider.__class__.__name__

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

            result = self.provider.calculate(request)

            if not result.success:
                LoggingEvents.calculation_failed(
                    logger,
                    provider=result.provider or provider_name,
                    error_code=self._get_error_code_value(
                        result.error_code,
                    ),
                    error_message=result.error or "Unknown error.",
                    exception=result.exception,
                )

                return result

            if result.routes:
                result.selected_route = self._select_best_route(
                    result,
                )

            LoggingEvents.calculation_completed(
                logger,
                provider=result.provider or provider_name,
                route_count=len(result.routes),
            )

            return result

        except DistanceCalculatorError as ex:
            LoggingEvents.calculation_failed(
                logger,
                provider=provider_name,
                error_code=self._get_error_code_value(
                    ex.error_code,
                ),
                error_message=str(ex),
                exception=ex,
                exception_is_active=True,
            )

            return RouteResult(
                success=False,
                request=request,
                provider=provider_name,
                error=str(ex),
                error_code=ex.error_code,
                context=ex.context,
                exception=ex,
            )

    @staticmethod
    def _get_error_code_value(
        error_code: object | None,
    ) -> str:
        """
        Convert an error code to a stable logging value.

        Supports Enum-based error codes and plain strings without
        coupling the service to a specific ErrorCode implementation.
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
        """Validate a route calculation request."""

        if not request.origin.strip():
            raise ValidationException(
                "Origin is empty.",
                context={
                    "field": "origin",
                },
            )

        if not request.destination.strip():
            raise ValidationException(
                "Destination is empty.",
                context={
                    "field": "destination",
                },
            )

        if (
            request.origin.strip()
            == request.destination.strip()
        ):
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