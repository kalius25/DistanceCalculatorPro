"""In-memory state-aware queue for route jobs."""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable, Iterator

from .models import RouteJob, RouteJobStatus


class BatchQueue:
    """Track route jobs and enforce valid status transitions."""

    def __init__(self, jobs: Iterable[RouteJob] = ()) -> None:
        self._jobs = list(jobs)
        self._pending = deque(
            job for job in self._jobs if job.status is RouteJobStatus.PENDING
        )

    def __len__(self) -> int:
        return len(self._jobs)

    def __iter__(self) -> Iterator[RouteJob]:
        return iter(self._jobs)

    def next_pending(self) -> RouteJob | None:
        if not self._pending:
            return None
        job = self._pending.popleft()
        job.status = RouteJobStatus.RUNNING
        return job

    def mark_done(self, job: RouteJob, distance_km: float | None = None) -> None:
        self._require(job, RouteJobStatus.RUNNING)
        job.status = RouteJobStatus.DONE
        job.result_distance_km = distance_km
        job.validation_error = None

    def mark_failed(self, job: RouteJob, message: str) -> None:
        self._require(job, RouteJobStatus.RUNNING)
        job.status = RouteJobStatus.FAILED
        job.validation_error = message

    def schedule_retry(self, job: RouteJob) -> None:
        if job.status not in {RouteJobStatus.RUNNING, RouteJobStatus.FAILED}:
            raise ValueError(f"Cannot retry job in state: {job.status.value}")
        job.retry_count += 1
        job.status = RouteJobStatus.RETRY
        job.status = RouteJobStatus.PENDING
        self._pending.append(job)

    def count(self, status: RouteJobStatus) -> int:
        return sum(job.status is status for job in self._jobs)

    @property
    def pending_count(self) -> int:
        return self.count(RouteJobStatus.PENDING)

    @property
    def ready_count(self) -> int:
        return self.pending_count

    @property
    def running_count(self) -> int:
        return self.count(RouteJobStatus.RUNNING)

    @property
    def done_count(self) -> int:
        return self.count(RouteJobStatus.DONE)

    @property
    def failed_count(self) -> int:
        return self.count(RouteJobStatus.FAILED)

    @property
    def terminal_count(self) -> int:
        return sum(
            self.count(status)
            for status in (
                RouteJobStatus.DONE,
                RouteJobStatus.FAILED,
                RouteJobStatus.SKIPPED,
                RouteJobStatus.INVALID,
            )
        )

    @property
    def skipped_count(self) -> int:
        return self.count(RouteJobStatus.SKIPPED)

    @property
    def invalid_count(self) -> int:
        return self.count(RouteJobStatus.INVALID)

    @staticmethod
    def _require(job: RouteJob, expected: RouteJobStatus) -> None:
        if job.status is not expected:
            raise ValueError(
                f"Expected job state {expected.value}, got {job.status.value}"
            )
