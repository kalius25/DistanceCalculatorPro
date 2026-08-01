from __future__ import annotations

from collections.abc import Callable, Iterable

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.services.calculation_service import CalculationService

ProgressCallback = Callable[[int, int, RouteRequest, RouteResult], None]
ControlCallback = Callable[[], bool]
WaitCallback = Callable[[], None]


class BatchCalculationService:
    def __init__(self, calculation_service: CalculationService):
        self.calculation_service = calculation_service

    def calculate(
        self,
        requests: Iterable[RouteRequest],
        progress_callback: ProgressCallback | None = None,
        should_stop: ControlCallback | None = None,
        wait_if_paused: WaitCallback | None = None,
    ) -> list[RouteResult]:
        request_list = list(requests)
        total = len(request_list)
        results: list[RouteResult] = []

        if not request_list:
            return results

        self.calculation_service.start_batch()
        try:
            for current, request in enumerate(request_list, start=1):
                if should_stop is not None and should_stop():
                    break
                if wait_if_paused is not None:
                    wait_if_paused()
                if should_stop is not None and should_stop():
                    break

                result = self.calculation_service.calculate(request)
                results.append(result)

                if progress_callback is not None:
                    progress_callback(current, total, request, result)
        finally:
            self.calculation_service.finish_batch()

        return results
