from __future__ import annotations

from collections.abc import Callable
from collections.abc import Iterable

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult

from app.services.calculation_service import CalculationService


ProgressCallback = Callable[
    [int, int, RouteRequest, RouteResult],
    None,
]


class BatchCalculationService:

    def __init__(
        self,
        calculation_service: CalculationService,
    ):
        self.calculation_service = calculation_service

    def calculate(
        self,
        requests: Iterable[RouteRequest],
        progress_callback: ProgressCallback | None = None,
    ) -> list[RouteResult]:

        requests = list(requests)

        total = len(requests)

        results: list[RouteResult] = []

        for current, request in enumerate(requests, start=1):

            result = self.calculation_service.calculate(
                request
            )

            results.append(result)

            if progress_callback:

                progress_callback(
                    current,
                    total,
                    request,
                    result,
                )

        return results