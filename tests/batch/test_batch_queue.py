import pytest

from app.batch import BatchQueue, RouteJob, RouteJobStatus


def job(status: RouteJobStatus = RouteJobStatus.PENDING) -> RouteJob:
    return RouteJob(2, "A", "B", "Distance", status=status)


def test_queue_tracks_counts_and_iteration() -> None:
    pending = job()
    skipped = job(RouteJobStatus.SKIPPED)
    invalid = job(RouteJobStatus.INVALID)
    queue = BatchQueue([pending, skipped, invalid])

    assert len(queue) == 3
    assert list(queue) == [pending, skipped, invalid]
    assert queue.pending_count == 1
    assert queue.ready_count == 1
    assert queue.skipped_count == 1
    assert queue.invalid_count == 1
    assert queue.count(RouteJobStatus.DONE) == 0


def test_queue_runs_completes_fails_and_retries_jobs() -> None:
    first = job()
    second = job()
    queue = BatchQueue([first, second])

    assert queue.next_pending() is first
    assert first.status is RouteJobStatus.RUNNING
    queue.mark_done(first, 8.6)
    assert first.status is RouteJobStatus.DONE
    assert first.result_distance_km == 8.6

    assert queue.next_pending() is second
    queue.mark_failed(second, "timeout")
    assert second.status is RouteJobStatus.FAILED
    assert second.validation_error == "timeout"
    queue.schedule_retry(second)
    assert second.status is RouteJobStatus.PENDING
    assert second.retry_count == 1
    assert queue.next_pending() is second
    queue.schedule_retry(second)
    assert queue.next_pending() is second
    queue.mark_done(second)
    assert queue.next_pending() is None


def test_queue_rejects_invalid_transitions() -> None:
    pending = job()
    queue = BatchQueue([pending])

    with pytest.raises(ValueError, match="Expected job state running"):
        queue.mark_done(pending)
    with pytest.raises(ValueError, match="Expected job state running"):
        queue.mark_failed(pending, "error")
    with pytest.raises(ValueError, match="Cannot retry job"):
        queue.schedule_retry(pending)
