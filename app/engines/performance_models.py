"""Runtime performance policy and metrics for browser route providers."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ProviderPerformancePolicy:
    """Control page reuse and proactive recycling for one browser batch."""

    page_recycle_interval: int = 50
    slow_request_threshold_seconds: float = 20.0

    def __post_init__(self) -> None:
        if self.page_recycle_interval < 1:
            raise ValueError("Page recycle interval must be at least one.")
        if self.slow_request_threshold_seconds <= 0:
            raise ValueError("Slow request threshold must be positive.")


@dataclass(frozen=True, slots=True)
class ProviderPerformanceSnapshot:
    """Immutable provider runtime metrics for one execution lifecycle."""

    requests_started: int
    requests_completed: int
    requests_failed: int
    pages_created: int
    pages_recycled: int
    slow_requests: int
    total_request_seconds: float
    average_request_seconds: float
    maximum_request_seconds: float


@dataclass(slots=True)
class ProviderPerformanceMetrics:
    """Mutable counters used internally by the provider."""

    requests_started: int = 0
    requests_completed: int = 0
    requests_failed: int = 0
    pages_created: int = 0
    pages_recycled: int = 0
    slow_requests: int = 0
    total_request_seconds: float = 0.0
    maximum_request_seconds: float = 0.0

    @property
    def snapshot(self) -> ProviderPerformanceSnapshot:
        completed_attempts = self.requests_completed + self.requests_failed
        average = (
            self.total_request_seconds / completed_attempts
            if completed_attempts
            else 0.0
        )
        return ProviderPerformanceSnapshot(
            requests_started=self.requests_started,
            requests_completed=self.requests_completed,
            requests_failed=self.requests_failed,
            pages_created=self.pages_created,
            pages_recycled=self.pages_recycled,
            slow_requests=self.slow_requests,
            total_request_seconds=self.total_request_seconds,
            average_request_seconds=average,
            maximum_request_seconds=self.maximum_request_seconds,
        )

    def record_duration(self, elapsed_seconds: float) -> None:
        elapsed = max(elapsed_seconds, 0.0)
        self.total_request_seconds += elapsed
        self.maximum_request_seconds = max(
            self.maximum_request_seconds,
            elapsed,
        )


__all__ = [
    "ProviderPerformanceMetrics",
    "ProviderPerformancePolicy",
    "ProviderPerformanceSnapshot",
]
