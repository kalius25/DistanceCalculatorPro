from __future__ import annotations

from collections.abc import Callable, Iterable

from app.logging import LoggingManager
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.services.calculation_service import CalculationService

logger = LoggingManager.get_logger(__name__)

ProgressCallback = Callable[
    [int, int, RouteRequest, RouteResult],
    None,
]
ControlCallback = Callable[[], bool]
WaitCallback = Callable[[], None]


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
        should_stop: ControlCallback | None = None,
        wait_if_paused: WaitCallback | None = None,
    ) -> list[RouteResult]:
        requests = list(requests)

        total = len(requests)

        results: list[RouteResult] = []

        for current, request in enumerate(requests, start=1):
            if should_stop is not None and should_stop():
                break
            if wait_if_paused is not None:
                wait_if_paused()
            if should_stop is not None and should_stop():
                break
            result = self.calculation_service.calculate(request)

            results.append(result)

            if progress_callback:
                progress_callback(
                    current,
                    total,
                    request,
                    result,
                )

        return results
