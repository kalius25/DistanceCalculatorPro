from __future__ import annotations

import pytest

from app.batch import BatchProgressTracker, RouteJob, RouteJobStatus


class Clock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value


def make_job(row_index: int, status: RouteJobStatus) -> RouteJob:
    return RouteJob(
        row_index=row_index,
        origin="A",
        destination="B",
        result_column="Distance",
        status=status,
    )


def test_progress_tracker_reports_runtime_metrics() -> None:
    clock = Clock()
    tracker = BatchProgressTracker(4, clock)

    clock.value = 10.0
    snapshot = tracker.record(make_job(2, RouteJobStatus.DONE))

    assert snapshot.total == 4
    assert snapshot.completed == 1
    assert snapshot.successful == 1
    assert snapshot.failed == 0
    assert snapshot.skipped == 0
    assert snapshot.remaining == 3
    assert snapshot.elapsed_seconds == 10.0
    assert snapshot.average_seconds_per_item == 10.0
    assert snapshot.items_per_minute == 6.0
    assert snapshot.eta_seconds == 30.0
    assert snapshot.percent_complete == 25.0

    clock.value = 20.0
    snapshot = tracker.record(make_job(3, RouteJobStatus.FAILED))

    assert snapshot.completed == 2
    assert snapshot.successful == 1
    assert snapshot.failed == 1
    assert snapshot.skipped == 0
    assert snapshot.percent_complete == 50.0


def test_progress_tracker_counts_skipped_separately() -> None:
    tracker = BatchProgressTracker(total=2)
    tracker.record(make_job(2, RouteJobStatus.DONE))
    snapshot = tracker.record(make_job(3, RouteJobStatus.SKIPPED))

    assert snapshot.completed == 2
    assert snapshot.successful == 1
    assert snapshot.failed == 0
    assert snapshot.skipped == 1
    assert snapshot.remaining == 0
    assert snapshot.percent_complete == 100.0


def test_progress_tracker_excludes_paused_time_and_handles_edge_cases() -> None:
    clock = Clock()
    tracker = BatchProgressTracker(0, clock)

    assert tracker.snapshot.percent_complete == 100.0
    assert tracker.snapshot.items_per_minute == 0.0
    assert tracker.snapshot.eta_seconds == 0.0
    assert tracker.snapshot.skipped == 0

    tracker.pause()
    tracker.pause()
    clock.value = 30.0
    assert tracker.snapshot.elapsed_seconds == 0.0
    tracker.resume()
    tracker.resume()

    clock.value = 35.0
    assert tracker.snapshot.elapsed_seconds == 5.0


def test_progress_tracker_rejects_negative_total_and_caps_values() -> None:
    with pytest.raises(ValueError, match="Total jobs cannot be negative"):
        BatchProgressTracker(-1)

    clock = Clock()
    tracker = BatchProgressTracker(1, clock)
    job = make_job(2, RouteJobStatus.DONE)
    tracker.record(job)
    tracker.record(job)

    assert tracker.snapshot.remaining == 0
    assert tracker.snapshot.percent_complete == 100.0


def test_progress_tracker_accepts_initial_counts() -> None:
    tracker = BatchProgressTracker(
        total=5,
        initial_completed=3,
        initial_successful=1,
        initial_failed=1,
        initial_skipped=1,
    )

    snapshot = tracker.snapshot

    assert snapshot.completed == 3
    assert snapshot.successful == 1
    assert snapshot.failed == 1
    assert snapshot.skipped == 1
    assert snapshot.remaining == 2
    assert snapshot.percent_complete == 60.0


def test_progress_tracker_rejects_invalid_initial_counts() -> None:
    with pytest.raises(
        ValueError,
        match="Initial completed jobs must be within total",
    ):
        BatchProgressTracker(total=5, initial_completed=6)

    with pytest.raises(
        ValueError,
        match="Initial completed jobs must be within total",
    ):
        BatchProgressTracker(total=5, initial_completed=-1)

    for values in (
        {"initial_successful": -1},
        {"initial_failed": -1},
        {"initial_skipped": -1},
    ):
        with pytest.raises(
            ValueError,
            match="Initial result counts cannot be negative",
        ):
            BatchProgressTracker(total=5, initial_completed=1, **values)

    with pytest.raises(
        ValueError,
        match="Initial result counts exceed completed jobs",
    ):
        BatchProgressTracker(
            total=5,
            initial_completed=2,
            initial_successful=1,
            initial_failed=1,
            initial_skipped=1,
        )
