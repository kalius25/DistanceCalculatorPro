from app.batch import RouteJob, RouteJobEvent, RouteJobStatus


def test_route_job_event_snapshots_job_and_normalizes_preview_row() -> None:
    job = RouteJob(7, "A", "B", "Distance")
    job.status = RouteJobStatus.RETRY
    job.attempt_count = 2
    job.retry_count = 1
    job.last_error = "timeout"

    event = RouteJobEvent.from_job(job)

    assert event.row_index == 7
    assert event.preview_row_index == 5
    assert event.status is RouteJobStatus.RETRY
    assert event.attempt_count == 2
    assert event.retry_count == 1
    assert event.message == "timeout"

    job.status = RouteJobStatus.DONE
    assert event.status is RouteJobStatus.RETRY


def test_route_job_event_clamps_preview_row_and_uses_validation_message() -> None:
    job = RouteJob(1, "", "B", "Distance", validation_error="Origin is required")

    event = RouteJobEvent.from_job(job)

    assert event.preview_row_index == 0
    assert event.message == "Origin is required"
