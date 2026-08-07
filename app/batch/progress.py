"""Runtime progress tracking for batch route calculation."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import monotonic

from app.batch.models import RouteJob, RouteJobStatus

Clock = Callable[[], float]


@dataclass(frozen=True, slots=True)
class ProgressSnapshot:
    """Immutable runtime metrics for one batch execution."""

    total: int
    completed: int
    successful: int
    failed: int
    skipped: int
    remaining: int
    elapsed_seconds: float
    average_seconds_per_item: float
    items_per_minute: float
    eta_seconds: float
    percent_complete: float
    invalid: int = 0
    retried: int = 0


class BatchProgressTracker:
    """Track elapsed time, throughput and ETA without counting pause time."""

    def __init__(
        self,
        total: int,
        clock: Clock = monotonic,
        initial_completed: int = 0,
        initial_successful: int = 0,
        initial_failed: int = 0,
        initial_skipped: int = 0,
        initial_invalid: int = 0,
        initial_retried: int = 0,
    ) -> None:
        if total < 0:
            raise ValueError("Total jobs cannot be negative.")
        if not 0 <= initial_completed <= total:
            raise ValueError("Initial completed jobs must be within total.")
        if any(
            value < 0
            for value in (
                initial_successful,
                initial_failed,
                initial_skipped,
                initial_invalid,
                initial_retried,
            )
        ):
            raise ValueError("Initial result counts cannot be negative.")
        if (
            initial_successful + initial_failed + initial_skipped + initial_invalid
            > initial_completed
        ):
            raise ValueError("Initial result counts exceed completed jobs.")
        self._total = total
        self._clock = clock
        self._started_at = clock()
        self._paused_at: float | None = None
        self._paused_seconds = 0.0
        self._completed = initial_completed
        self._successful = initial_successful
        self._failed = initial_failed
        self._skipped = initial_skipped
        self._invalid = initial_invalid
        self._retried = initial_retried

    @property
    def snapshot(self) -> ProgressSnapshot:
        elapsed = self._elapsed_seconds()
        average = elapsed / self._completed if self._completed else 0.0
        rate = self._completed / elapsed * 60.0 if elapsed > 0 else 0.0
        remaining = max(self._total - self._completed, 0)
        eta = average * remaining if self._completed else 0.0
        percent = (
            min(self._completed / self._total * 100.0, 100.0) if self._total else 100.0
        )
        return ProgressSnapshot(
            total=self._total,
            completed=self._completed,
            successful=self._successful,
            failed=self._failed,
            skipped=self._skipped,
            remaining=remaining,
            elapsed_seconds=elapsed,
            average_seconds_per_item=average,
            items_per_minute=rate,
            eta_seconds=eta,
            percent_complete=percent,
            invalid=self._invalid,
            retried=self._retried,
        )

    def record(self, job: RouteJob) -> ProgressSnapshot:
        """Record one terminal job and return the updated metrics."""
        self._completed += 1
        if job.status is RouteJobStatus.DONE:
            self._successful += 1
        elif job.status is RouteJobStatus.SKIPPED:
            self._skipped += 1
        elif job.status is RouteJobStatus.INVALID:
            self._invalid += 1
        else:
            self._failed += 1
        self._retried += job.retry_count
        return self.snapshot

    def pause(self) -> None:
        if self._paused_at is None:
            self._paused_at = self._clock()

    def resume(self) -> None:
        if self._paused_at is None:
            return
        self._paused_seconds += self._clock() - self._paused_at
        self._paused_at = None

    def _elapsed_seconds(self) -> float:
        end = self._paused_at if self._paused_at is not None else self._clock()
        return max(end - self._started_at - self._paused_seconds, 0.0)
