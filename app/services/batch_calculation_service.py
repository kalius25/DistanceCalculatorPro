from __future__ import annotations

from collections.abc import Callable, Iterable

from app.batch.batch_queue import BatchQueue
from app.batch.models import RouteJob, RouteJobStatus
from app.batch.result_writer import BaseResultWriter
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.services.calculation_service import CalculationService

ProgressCallback = Callable[[int, int, RouteRequest, RouteResult], None]
QueueProgressCallback = Callable[[int, int, RouteJob, RouteResult], None]
ControlCallback = Callable[[], bool]
WaitCallback = Callable[[], None]


class BatchCalculationService:
    """Execute route calculations using requests or a state-aware queue."""

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
                if self._should_stop(should_stop):
                    break
                if wait_if_paused is not None:
                    wait_if_paused()
                if self._should_stop(should_stop):
                    break

                result = self.calculation_service.calculate(request)
                results.append(result)

                if progress_callback is not None:
                    progress_callback(current, total, request, result)
        finally:
            self.calculation_service.finish_batch()

        return results

    def calculate_queue(
        self,
        queue: BatchQueue,
        progress_callback: QueueProgressCallback | None = None,
        should_stop: ControlCallback | None = None,
        wait_if_paused: WaitCallback | None = None,
        result_writer: BaseResultWriter | None = None,
    ) -> list[RouteResult]:
        """Process pending jobs while updating state and writing results."""
        total = queue.pending_count
        results: list[RouteResult] = []
        self._write_existing_results(queue, result_writer)
        if total == 0:
            if result_writer is not None:
                result_writer.flush()
            return results

        self.calculation_service.start_batch()
        try:
            current = 0
            while queue.pending_count > 0 and not self._should_stop(
                should_stop
            ):
                if wait_if_paused is not None:
                    wait_if_paused()
                if self._should_stop(should_stop):
                    break

                job = queue.next_pending()
                if job is None:
                    break
                current += 1

                request = self._request_from_job(job)
                try:
                    result = self.calculation_service.calculate(request)
                except Exception as error:
                    queue.mark_failed(job, str(error))
                    if result_writer is not None:
                        result_writer.write(job)
                    raise

                results.append(result)
                if result.success:
                    best_route = result.best_route
                    distance_km = (
                        best_route.distance_km if best_route is not None else None
                    )
                    queue.mark_done(job, distance_km)
                else:
                    queue.mark_failed(job, result.error or "Unknown error.")

                if result_writer is not None:
                    result_writer.write(job)

                if progress_callback is not None:
                    progress_callback(current, total, job, result)
        finally:
            if result_writer is not None:
                result_writer.flush()
            self.calculation_service.finish_batch()

        return results

    @staticmethod
    def _write_existing_results(
        queue: BatchQueue,
        result_writer: BaseResultWriter | None,
    ) -> None:
        if result_writer is None:
            return
        for job in queue:
            if job.status in {RouteJobStatus.DONE, RouteJobStatus.INVALID}:
                result_writer.write(job)

    @staticmethod
    def _request_from_job(job: RouteJob) -> RouteRequest:
        return RouteRequest(
            origin=job.origin,
            destination=job.destination,
            travel_mode=job.travel_mode,
            toll_preference=job.toll_preference,
            ferry_preference=job.ferry_preference,
            highway_preference=job.highway_preference,
            metadata={
                **job.metadata,
                "row_number": job.row_index,
                "result_column": job.result_column,
            },
        )

    @staticmethod
    def _should_stop(callback: ControlCallback | None) -> bool:
        return callback is not None and callback()
