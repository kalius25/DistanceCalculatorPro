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
    assert queue.running_count == 0
    assert queue.done_count == 0
    assert queue.failed_count == 0
    assert queue.terminal_count == 2


def test_queue_runs_completes_fails_and_retries_jobs() -> None:
    first = job()
    second = job()
    queue = BatchQueue([first, second])

    assert queue.next_pending() is first
    assert first.status is RouteJobStatus.RUNNING
    assert queue.running_count == 1
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


def test_queue_records_and_resumes_transient_retry() -> None:
    queue = BatchQueue([job()])
    route_job = queue.next_pending()
    assert route_job is not None

    queue.mark_retry(route_job, "timeout")

    assert route_job.status is RouteJobStatus.RETRY
    assert route_job.retry_count == 1
    assert route_job.last_error == "timeout"
    assert route_job.validation_error == "timeout"

    queue.resume_retry(route_job)
    assert route_job.status is RouteJobStatus.RUNNING


def test_queue_schedules_existing_retry_without_double_counting() -> None:
    queue = BatchQueue([job()])
    route_job = queue.next_pending()
    assert route_job is not None
    queue.mark_retry(route_job, "timeout")

    queue.schedule_retry(route_job)

    assert route_job.status is RouteJobStatus.PENDING
    assert route_job.retry_count == 1
    assert queue.next_pending() is route_job


def test_queue_rejects_invalid_retry_state_transitions() -> None:
    queue = BatchQueue([job()])
    pending = next(iter(queue))

    import pytest

    with pytest.raises(ValueError, match="Expected job state running"):
        queue.mark_retry(pending, "timeout")
    with pytest.raises(ValueError, match="Expected job state retry"):
        queue.resume_retry(pending)


def test_queue_builds_failed_only_retry_queue() -> None:
    done = RouteJob(2, "A", "B", "Distance")
    done.status = RouteJobStatus.DONE
    failed = RouteJob(3, "C", "D", "Distance")
    failed.status = RouteJobStatus.FAILED
    failed.validation_error = "timeout"
    failed.last_error = "timeout"

    retry_queue = BatchQueue((done, failed)).failed_only()

    assert len(retry_queue) == 1
    retry_job = next(iter(retry_queue))
    assert retry_job.status is RouteJobStatus.PENDING
    assert retry_job.validation_error is None
    assert retry_job.last_error is None
    assert retry_job.metadata["retry_failed_only"] is True
    assert failed.status is RouteJobStatus.FAILED
