from __future__ import annotations

import json
from pathlib import Path

from app.batch import (
    BatchProgressTracker,
    BatchQueue,
    BatchSummary,
    BatchSummaryWriter,
    RouteJob,
    RouteJobStatus,
)


def test_summary_counts_queue_and_runtime_values(tmp_path: Path) -> None:
    done = RouteJob(2, "A", "B", "Distance")
    done.status = RouteJobStatus.DONE
    done.retry_count = 1
    done.metadata["resumed_existing_result"] = True

    failed = RouteJob(3, "C", "D", "Distance")
    failed.status = RouteJobStatus.FAILED
    failed.retry_count = 2

    skipped = RouteJob(4, "", "D", "Distance")
    skipped.status = RouteJobStatus.SKIPPED

    invalid = RouteJob(5, "10,999", "D", "Distance")
    invalid.status = RouteJobStatus.INVALID

    queue = BatchQueue((done, failed, skipped, invalid))
    tracker = BatchProgressTracker(
        total=4,
        initial_completed=4,
        initial_successful=1,
        initial_failed=1,
        initial_skipped=1,
    )

    summary = BatchSummary.from_queue(
        queue,
        tracker.snapshot,
        tmp_path / "routes.result.xlsx",
        stopped=True,
    )

    assert summary.total == 4
    assert summary.completed == 4
    assert summary.successful == 1
    assert summary.failed == 1
    assert summary.skipped == 1
    assert summary.invalid == 1
    assert summary.resumed == 1
    assert summary.retry_count == 3
    assert summary.stopped


def test_summary_writer_persists_json(tmp_path: Path) -> None:
    summary = BatchSummary(
        total=2,
        completed=2,
        successful=1,
        failed=1,
        skipped=0,
        invalid=0,
        resumed=0,
        retry_count=2,
        elapsed_seconds=12.5,
        items_per_minute=9.6,
        output_file="routes.result.csv",
    )

    path = BatchSummaryWriter(tmp_path).write(summary)
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.parent == tmp_path
    assert payload["successful"] == 1
    assert payload["failed"] == 1
    assert payload["created_at"]
