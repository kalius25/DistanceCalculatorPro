from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from time import sleep

from app.batch.batch_queue import BatchQueue
from app.batch.models import RouteJob, RouteJobStatus
from app.batch.result_writer import BaseResultWriter
from app.batch.retry_decision import RetryDecision
from app.batch.retry_policy import RetryPolicy
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.services.calculation_service import CalculationService

ProgressCallback = Callable[[int, int, RouteRequest, RouteResult], None]
QueueProgressCallback = Callable[[int, int, RouteJob, RouteResult], None]
ControlCallback = Callable[[], bool]
WaitCallback = Callable[[], None]
SleepCallback = Callable[[float], None]


class BatchCalculationService:
    """Execute route calculations using requests or a state-aware queue."""

    def __init__(
        self,
        calculation_service: CalculationService,
        retry_policy: RetryPolicy | None = None,
        retry_decision: RetryDecision | None = None,
        sleep_callback: SleepCallback = sleep,
    ) -> None:
        self.calculation_service = calculation_service
        self.retry_policy = retry_policy or RetryPolicy()
        self.retry_decision = retry_decision or RetryDecision()
        self._sleep = sleep_callback

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
                job.started_at = job.started_at or datetime.now(UTC)

                try:
                    result = self._calculate_job_with_retry(
                        queue,
                        job,
                        should_stop,
                        wait_if_paused,
                    )
                except Exception:
                    if result_writer is not None:
                        result_writer.write(job)
                    raise
                if result is None:
                    queue.schedule_retry(job)
                    break

                results.append(result)
                job.finished_at = datetime.now(UTC)
                if result.success:
                    best_route = result.best_route
                    distance_km = (
                        best_route.distance_km if best_route is not None else None
                    )
                    queue.mark_done(job, distance_km)
                else:
                    message = result.error or "Unknown error."
                    job.last_error = message
                    queue.mark_failed(job, message)

                if result_writer is not None:
                    result_writer.write(job)

                if progress_callback is not None:
                    progress_callback(current, total, job, result)
        finally:
            if result_writer is not None:
                result_writer.flush()
            self.calculation_service.finish_batch()

        return results

    def _calculate_job_with_retry(
        self,
        queue: BatchQueue,
        job: RouteJob,
        should_stop: ControlCallback | None,
        wait_if_paused: WaitCallback | None,
    ) -> RouteResult | None:
        request = self._request_from_job(job)
        while True:
            job.attempt_count += 1
            try:
                result = self.calculation_service.calculate(request)
            except Exception as error:
                message = str(error)
                job.last_error = message
                if not self._can_retry_exception(job, error):
                    queue.mark_failed(job, message)
                    job.finished_at = datetime.now(UTC)
                    raise
                queue.mark_retry(job, message)
                if not self._wait_before_retry(
                    queue,
                    job,
                    should_stop,
                    wait_if_paused,
                ):
                    return None
                continue

            if result.success or not self._can_retry_result(job, result):
                return result

            message = result.error or "Unknown error."
            queue.mark_retry(job, message)
            if not self._wait_before_retry(
                queue,
                job,
                should_stop,
                wait_if_paused,
            ):
                return None

    def _can_retry_result(self, job: RouteJob, result: RouteResult) -> bool:
        return self.retry_policy.can_retry(
            job.attempt_count
        ) and self.retry_decision.should_retry_result(result)

    def _can_retry_exception(self, job: RouteJob, error: Exception) -> bool:
        return self.retry_policy.can_retry(
            job.attempt_count
        ) and self.retry_decision.should_retry_exception(error)

    def _wait_before_retry(
        self,
        queue: BatchQueue,
        job: RouteJob,
        should_stop: ControlCallback | None,
        wait_if_paused: WaitCallback | None,
    ) -> bool:
        delay = self.retry_policy.delay_for_retry(job.retry_count)
        remaining = delay
        while remaining > 0:
            if wait_if_paused is not None:
                wait_if_paused()
            if self._should_stop(should_stop):
                return False
            interval = min(remaining, 0.1)
            self._sleep(interval)
            remaining -= interval
        if self._should_stop(should_stop):
            return False
        queue.resume_retry(job)
        return True

    @staticmethod
    def _write_existing_results(
        queue: BatchQueue,
        result_writer: BaseResultWriter | None,
    ) -> None:
        if result_writer is None:
            return
        for job in queue:
            should_write_done = (
                job.status is RouteJobStatus.DONE
                and not job.metadata.get("resumed_existing_result", False)
            )
            if should_write_done or job.status is RouteJobStatus.INVALID:
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
