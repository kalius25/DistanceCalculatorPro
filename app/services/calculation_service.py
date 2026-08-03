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
    Coordinate route calculation.
    """

    def __init__(
        self,
        provider: BaseProvider,
    ) -> None:
        self._provider = provider

    def start_batch(self) -> None:
        """Start provider resources for one batch."""
        self._provider.start_batch()

    def finish_batch(self) -> None:
        """Release provider resources after one batch."""
        self._provider.finish_batch()

    @property
    def provider(self) -> BaseProvider:
        """
        Compatibility property (CFG-013).
        """
        return self._provider

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:

        self._validate(request)

        provider_name = self._provider.__class__.__name__

        LoggingEvents.calculation_started(
            logger,
            origin=request.origin,
            destination=request.destination,
        )

        LoggingEvents.provider_selected(
            logger,
            provider=provider_name,
        )

        try:
            result = self._provider.calculate(request)

        except DistanceCalculatorError as ex:

            LoggingEvents.calculation_failed(
                logger,
                provider=provider_name,
                error_code=ex.error_code.value,
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

        if not result.success:

            LoggingEvents.calculation_failed(
                logger,
                provider=result.provider or provider_name,
                error_code=(
                    result.error_code.value if result.error_code else "UNKNOWN_ERROR"
                ),
                error_message=result.error or "Unknown error.",
                exception=result.exception,
            )

            return result

        if result.routes:
            result.selected_route = min(
                range(len(result.routes)),
                key=lambda i: (
                    result.routes[i].duration_minutes,
                    result.routes[i].distance_km,
                ),
            )

        LoggingEvents.calculation_completed(
            logger,
            provider=result.provider or provider_name,
            route_count=len(result.routes),
        )

        return result

    @staticmethod
    def _validate(
        request: RouteRequest,
    ) -> None:

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


__all__ = [
    "CalculationService",
]
