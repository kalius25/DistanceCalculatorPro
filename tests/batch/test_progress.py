from __future__ import annotations

from app.batch import BatchProgressTracker, RouteJob, RouteJobStatus


class Clock:
    def __init__(self) -> None:
        self.value = 0.0

    def __call__(self) -> float:
        return self.value


def test_progress_tracker_reports_runtime_metrics() -> None:
    clock = Clock()
    tracker = BatchProgressTracker(4, clock)
    job = RouteJob(2, "A", "B", "Distance")
    job.status = RouteJobStatus.DONE

    clock.value = 10.0
    snapshot = tracker.record(job)

    assert snapshot.total == 4
    assert snapshot.completed == 1
    assert snapshot.successful == 1
    assert snapshot.failed == 0
    assert snapshot.remaining == 3
    assert snapshot.elapsed_seconds == 10.0
    assert snapshot.average_seconds_per_item == 10.0
    assert snapshot.items_per_minute == 6.0
    assert snapshot.eta_seconds == 30.0
    assert snapshot.percent_complete == 25.0

    failed = RouteJob(3, "C", "D", "Distance")
    failed.status = RouteJobStatus.FAILED
    clock.value = 20.0
    snapshot = tracker.record(failed)

    assert snapshot.completed == 2
    assert snapshot.successful == 1
    assert snapshot.failed == 1
    assert snapshot.percent_complete == 50.0


def test_progress_tracker_excludes_paused_time_and_handles_edge_cases() -> None:
    clock = Clock()
    tracker = BatchProgressTracker(0, clock)

    assert tracker.snapshot.percent_complete == 100.0
    assert tracker.snapshot.items_per_minute == 0.0
    assert tracker.snapshot.eta_seconds == 0.0

    tracker.pause()
    tracker.pause()
    clock.value = 30.0
    assert tracker.snapshot.elapsed_seconds == 0.0
    tracker.resume()
    tracker.resume()

    clock.value = 35.0
    assert tracker.snapshot.elapsed_seconds == 5.0


def test_progress_tracker_rejects_negative_total_and_caps_values() -> None:
    import pytest

    with pytest.raises(ValueError, match="Total jobs cannot be negative"):
        BatchProgressTracker(-1)

    clock = Clock()
    tracker = BatchProgressTracker(1, clock)
    job = RouteJob(2, "A", "B", "Distance")
    job.status = RouteJobStatus.DONE
    tracker.record(job)
    tracker.record(job)

    assert tracker.snapshot.remaining == 0
    assert tracker.snapshot.percent_complete == 100.0
