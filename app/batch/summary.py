"""Batch execution summary models and JSON persistence."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path

from .batch_queue import BatchQueue
from .progress import ProgressSnapshot


@dataclass(frozen=True, slots=True)
class BatchSummary:
    """Immutable final statistics for one batch execution."""

    total: int
    completed: int
    successful: int
    failed: int
    skipped: int
    invalid: int
    resumed: int
    retry_count: int
    elapsed_seconds: float
    items_per_minute: float
    output_file: str
    stopped: bool = False

    @classmethod
    def from_queue(
        cls,
        queue: BatchQueue,
        metrics: ProgressSnapshot,
        output_file: str | Path,
        *,
        stopped: bool = False,
    ) -> BatchSummary:
        resumed = sum(
            bool(job.metadata.get("resumed_existing_result")) for job in queue
        )
        return cls(
            total=len(queue),
            completed=queue.terminal_count,
            successful=queue.done_count,
            failed=queue.failed_count,
            skipped=queue.skipped_count,
            invalid=queue.invalid_count,
            resumed=resumed,
            retry_count=sum(job.retry_count for job in queue),
            elapsed_seconds=metrics.elapsed_seconds,
            items_per_minute=metrics.items_per_minute,
            output_file=str(output_file),
            stopped=stopped,
        )


class BatchSummaryWriter:
    """Persist batch summaries as timestamped JSON documents."""

    def __init__(self, output_directory: str | Path = "logs/batch") -> None:
        self._output_directory = Path(output_directory)

    def write(self, summary: BatchSummary) -> Path:
        self._output_directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
        path = self._output_directory / f"batch-summary-{timestamp}.json"
        payload = asdict(summary)
        payload["created_at"] = datetime.now(UTC).isoformat()
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


__all__ = ["BatchSummary", "BatchSummaryWriter"]
