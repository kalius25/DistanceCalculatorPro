from __future__ import annotations

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider

class RouteService:
    """Business service for route calculation."""

    def __init__(
        self,
        provider: BaseProvider,
    ) -> None:
        self._provider = provider

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:
        """
        Calculate routes and select the best route.
        """

        error = self._validate_request(request)

        if error is not None:
            return RouteResult(
                success=False,
                request=request,
                provider="",
                error=error,
            )

        result = self._provider.calculate(request)

        if not result.success:
            return result

        self._select_best_route(result)

        return result

    @staticmethod
    def _validate_request(
        request: RouteRequest,
    ) -> str | None:
        """
        Validate a route request.

        Returns
        -------
        str | None
            Error message if invalid.
        """

        origin = request.origin.strip()
        destination = request.destination.strip()

        if not origin:
            return "Origin is empty."

        if not destination:
            return "Destination is empty."

        if origin == destination:
            return "Origin and destination cannot be the same."

        return None

    @staticmethod
    def _select_best_route(
        result: RouteResult,
    ) -> None:
        """
        Select the best route.

        Strategy
        --------
        1. Shortest duration
        2. Shortest distance
        """

        if not result.routes:
            return

        result.selected_route = min(
            range(len(result.routes)),
            key=lambda index: (
                result.routes[index].duration_minutes,
                result.routes[index].distance_km,
            ),
        )