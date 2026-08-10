"""Immutable row-level execution events for batch processing."""

from __future__ import annotations

from dataclasses import dataclass

from .models import RouteJob, RouteJobStatus


@dataclass(frozen=True, slots=True)
class RouteJobEvent:
    """Snapshot one route-job state transition for presentation consumers."""

    row_index: int
    preview_row_index: int
    status: RouteJobStatus
    attempt_count: int
    retry_count: int
    message: str | None = None

    @classmethod
    def from_job(cls, job: RouteJob) -> RouteJobEvent:
        """Create an immutable event without retaining the mutable job object."""
        return cls(
            row_index=job.row_index,
            preview_row_index=max(job.row_index - 2, 0),
            status=job.status,
            attempt_count=job.attempt_count,
            retry_count=job.retry_count,
            message=job.last_error or job.validation_error,
        )


__all__ = ["RouteJobEvent"]
