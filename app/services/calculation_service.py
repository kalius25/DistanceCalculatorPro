from __future__ import annotations

import traceback

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider


class CalculationService:

    def __init__(self, provider: BaseProvider):
        self.provider = provider

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:

        try:

            self._validate(request)

            result = self.provider.calculate(request)

            if result.routes:
                result.selected_route = self._select_best_route(result)

            return result

        except Exception as ex:

            traceback.print_exc()

            return RouteResult(
                success=False,
                request=request,
                provider=self.provider.__class__.__name__,
                error=str(ex),
            )

    @staticmethod
    def _validate(request: RouteRequest):

        if not request.origin.strip():
            raise ValueError("Origin is empty.")

        if not request.destination.strip():
            raise ValueError("Destination is empty.")

    @staticmethod
    def _select_best_route(result: RouteResult) -> int:

        best_index = 0
        best_minutes = result.routes[0].duration_minutes

        for index, route in enumerate(result.routes):

            if route.duration_minutes < best_minutes:
                best_minutes = route.duration_minutes
                best_index = index

        return best_index