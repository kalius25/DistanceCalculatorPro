from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.batch import BatchQueue, RouteJob, RouteJobStatus
from app.batch.summary import BatchSummary
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.presentation.execution.job import CalculationJob
from app.presentation.execution.worker import (
    CalculationExecutionCoordinator,
    CalculationWorker,
)


def make_worker_components() -> tuple[
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    job = MagicMock(spec=CalculationJob)
    builder = MagicMock()
    batch = MagicMock()
    writer = MagicMock()
    writer.output_path = "routes.result.xlsx"
    writer.__enter__.return_value = writer
    writer_factory = MagicMock()
    writer_factory.create.return_value = writer
    return job, builder, batch, writer, writer_factory


def test_worker_completes_and_emits_summary_and_failed_queue(
    qtbot: object,
) -> None:
    job, builder, batch, writer, writer_factory = make_worker_components()
    request = RouteRequest("A", "B")
    result = RouteResult(True, request, "Google")
    route_job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([route_job])
    builder.build_queue.return_value = queue

    def calculate_queue(
        received_queue: object,
        progress_callback: object,
        **kwargs: object,
    ) -> list[RouteResult]:
        assert received_queue is queue
        route_job.status = RouteJobStatus.DONE
        progress_callback(1, 1, route_job, result)  # type: ignore[operator]
        return [result]

    batch.calculate_queue.side_effect = calculate_queue
    summary_writer = MagicMock()
    worker = CalculationWorker(
        job,
        builder,
        batch,
        writer_factory,
        summary_writer,
    )

    with (
        qtbot.waitSignal(worker.progress),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.metrics),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.completed),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.summary) as summary_signal,  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.failed_queue) as queue_signal,  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.finished),  # type: ignore[attr-defined]
    ):
        worker.run()

    summary = summary_signal.args[0]
    assert isinstance(summary, BatchSummary)
    assert summary.successful == 1
    assert queue_signal.args[0].pending_count == 0
    summary_writer.write.assert_called_once_with(summary)
    writer_factory.create.assert_called_once_with(
        job.file_path,
        job.sheet_name,
        resume_from_output=False,
        output_path=job.output_path,
    )


def test_worker_uses_override_queue_and_emits_stopped_summary(
    qtbot: object,
) -> None:
    job, builder, batch, _writer, writer_factory = make_worker_components()
    failed = RouteJob(2, "A", "B", "Distance")
    failed.status = RouteJobStatus.FAILED
    source_queue = BatchQueue([failed])
    retry_queue = source_queue.failed_only()
    batch.calculate_queue.return_value = []
    summary_writer = MagicMock()
    worker = CalculationWorker(
        job,
        builder,
        batch,
        writer_factory,
        summary_writer,
        retry_queue,
    )
    worker.request_stop()

    with (
        qtbot.waitSignal(worker.stopped),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.summary) as summary_signal,  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.finished),  # type: ignore[attr-defined]
    ):
        worker.run()

    builder.build_queue.assert_not_called()
    assert summary_signal.args[0].stopped is True
    writer_factory.create.assert_called_once_with(
        job.file_path,
        job.sheet_name,
        resume_from_output=True,
        output_path=job.output_path,
    )


def test_worker_failed_and_control_methods(qtbot: object) -> None:
    job, builder, batch, _writer, writer_factory = make_worker_components()
    worker = CalculationWorker(job, builder, batch, writer_factory)
    builder.build_queue.side_effect = ValueError("bad job")

    with (
        qtbot.waitSignal(  # type: ignore[attr-defined]
            worker.failed,
            check_params_cb=lambda message: message == "bad job",
        ),
        qtbot.waitSignal(worker.finished),  # type: ignore[attr-defined]
    ):
        worker.run()

    worker = CalculationWorker(job, MagicMock(), MagicMock())
    worker.request_pause()
    with patch.object(
        worker._condition,
        "wait",
        side_effect=lambda: setattr(worker, "_paused", False),
    ) as wait:
        worker._wait_if_paused()
    wait.assert_called_once_with()
    worker.request_resume()
    worker.request_stop()
    assert worker._should_stop()
    worker._paused = True
    worker._wait_if_paused()


def test_worker_progress_helper_emits_metrics(qtbot: object) -> None:
    worker = CalculationWorker(MagicMock(), MagicMock(), MagicMock())
    request = RouteRequest("A", "B")
    route_job = RouteJob(2, "A", "B", "Distance")
    result = RouteResult(True, request, "Google")

    with qtbot.waitSignal(worker.progress):  # type: ignore[attr-defined]
        worker._on_progress(1, 2, route_job, result)

    route_job.status = RouteJobStatus.SKIPPED
    from app.batch.progress import BatchProgressTracker

    worker._progress_tracker = BatchProgressTracker(2, clock=lambda: 1.0)
    worker.request_pause()
    worker.request_resume()
    with (
        qtbot.waitSignal(worker.progress),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.metrics) as metrics_signal,  # type: ignore[attr-defined]
    ):
        worker._on_progress(1, 2, route_job, result)

    assert metrics_signal.args[0].skipped == 1


def test_coordinator_starts_retries_controls_and_clears_worker() -> None:
    coordinator = CalculationExecutionCoordinator(MagicMock(), MagicMock())
    thread = MagicMock()
    worker = MagicMock()
    for signal_name in (
        "progress",
        "row_event",
        "metrics",
        "completed",
        "stopped",
        "failed",
        "output_write_failed",
        "summary",
        "failed_queue",
        "finished",
    ):
        setattr(worker, signal_name, MagicMock())
    thread.started = MagicMock()
    thread.finished = MagicMock()

    with (
        patch(
            "app.presentation.execution.worker.QThread",
            return_value=thread,
        ),
        patch(
            "app.presentation.execution.worker.CalculationWorker",
            return_value=worker,
        ),
    ):
        job = MagicMock()
        assert coordinator.start(job)
        assert not coordinator.start(MagicMock())

    worker.moveToThread.assert_called_once_with(thread)
    thread.start.assert_called_once_with()
    coordinator.pause()
    coordinator.resume()
    coordinator.stop()
    worker.request_pause.assert_called_once_with()
    worker.request_resume.assert_called_once_with()
    worker.request_stop.assert_called_once_with()

    coordinator._clear_worker()
    assert not coordinator.is_running
    assert not coordinator.retry_failed()

    failed_job = RouteJob(2, "A", "B", "Distance")
    failed_job.status = RouteJobStatus.FAILED
    coordinator._last_job = job
    coordinator._store_failed_queue(BatchQueue([failed_job]).failed_only())
    with patch.object(coordinator, "_start_worker", return_value=True) as start:
        assert coordinator.retry_failed()
    start.assert_called_once()

    coordinator._store_failed_queue(object())
    assert coordinator._failed_queue is None
    coordinator.pause()
    coordinator.resume()
    coordinator.stop()


def test_coordinator_shutdown_stops_waits_and_releases_resources() -> None:
    callback = MagicMock()
    coordinator = CalculationExecutionCoordinator(
        MagicMock(),
        MagicMock(),
        shutdown_callback=callback,
    )
    thread = MagicMock()
    thread.wait.return_value = True
    worker = MagicMock()
    coordinator._thread = thread
    coordinator._worker = worker

    assert coordinator.shutdown(timeout_ms=123)

    worker.request_stop.assert_called_once_with()
    thread.wait.assert_called_once_with(123)
    callback.assert_called_once_with()
    assert not coordinator.is_running
    assert coordinator.shutdown()
    callback.assert_called_once_with()


def test_coordinator_shutdown_reports_worker_timeout() -> None:
    callback = MagicMock()
    coordinator = CalculationExecutionCoordinator(
        MagicMock(),
        MagicMock(),
        shutdown_callback=callback,
    )
    thread = MagicMock()
    thread.wait.return_value = False
    worker = MagicMock()
    coordinator._thread = thread
    coordinator._worker = worker

    assert not coordinator.shutdown(timeout_ms=10)

    worker.request_stop.assert_called_once_with()
    callback.assert_not_called()
    assert coordinator.is_running


def test_coordinator_shutdown_without_active_thread_is_safe() -> None:
    coordinator = CalculationExecutionCoordinator(MagicMock(), MagicMock())

    assert coordinator.shutdown()
    assert coordinator.shutdown()


def test_worker_emits_structured_output_write_failure(qtbot: object) -> None:
    from pathlib import Path

    from app.batch.file_access import OutputWriteError

    job = CalculationJob(
        "routes.xlsx",
        "Routes",
        MagicMock(),
    )
    builder = MagicMock()
    queue = BatchQueue([])
    builder.build_queue.return_value = queue
    writer_factory = MagicMock()
    writer_factory.create.side_effect = OutputWriteError(
        Path("routes.result.xlsx"),
        "write",
        "locked",
    )
    worker = CalculationWorker(job, builder, MagicMock(), writer_factory)

    with (
        qtbot.waitSignal(worker.output_write_failed) as signal,  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.finished),  # type: ignore[attr-defined]
    ):
        worker.run()

    assert isinstance(signal.args[0], OutputWriteError)


def test_worker_passes_explicit_output_path_and_coordinator_can_retry() -> None:
    job = CalculationJob(
        "routes.xlsx",
        "Routes",
        MagicMock(),
        output_path="alternate.xlsx",
    )
    builder = MagicMock()
    builder.build_queue.return_value = BatchQueue([])
    writer = MagicMock()
    writer.output_path = "alternate.xlsx"
    writer.__enter__.return_value = writer
    writer_factory = MagicMock()
    writer_factory.create.return_value = writer
    worker = CalculationWorker(job, builder, MagicMock(), writer_factory)
    worker.run()

    writer_factory.create.assert_called_once_with(
        "routes.xlsx",
        "Routes",
        resume_from_output=False,
        output_path="alternate.xlsx",
    )

    coordinator = CalculationExecutionCoordinator(MagicMock(), MagicMock())
    coordinator._last_job = CalculationJob("routes.xlsx", "Routes", MagicMock())
    with patch.object(coordinator, "_start_worker", return_value=True) as start:
        assert coordinator.retry_with_output("new.xlsx")
    retry_job = start.call_args.args[0]
    assert retry_job.output_path == "new.xlsx"
    coordinator._last_job = None
    assert not coordinator.retry_with_output("blocked.xlsx")
    coordinator._last_job = job
    coordinator._thread = MagicMock()
    assert not coordinator.retry_with_output("blocked.xlsx")


def test_worker_emits_initial_terminal_row_events(qtbot: object) -> None:
    from app.batch import RouteJobEvent

    job, builder, batch, _writer, writer_factory = make_worker_components()
    invalid = RouteJob(2, "", "B", "Distance", status=RouteJobStatus.INVALID)
    skipped = RouteJob(3, "C", "D", "Distance", status=RouteJobStatus.SKIPPED)
    queue = BatchQueue([invalid, skipped])
    builder.build_queue.return_value = queue
    batch.calculate_queue.return_value = []
    worker = CalculationWorker(job, builder, batch, writer_factory)
    received: list[RouteJobEvent] = []
    worker.row_event.connect(received.append)

    with qtbot.waitSignal(worker.finished):  # type: ignore[attr-defined]
        worker.run()

    assert [event.status for event in received] == [
        RouteJobStatus.INVALID,
        RouteJobStatus.SKIPPED,
    ]
    assert [event.preview_row_index for event in received] == [0, 1]


def test_worker_relays_service_row_event(qtbot: object) -> None:
    from app.batch import RouteJobEvent

    worker = CalculationWorker(MagicMock(), MagicMock(), MagicMock())
    route_job = RouteJob(4, "A", "B", "Distance", status=RouteJobStatus.RUNNING)
    event = RouteJobEvent.from_job(route_job)

    with qtbot.waitSignal(  # type: ignore[attr-defined]
        worker.row_event,
        check_params_cb=lambda received: received == event,
    ):
        worker._on_row_event(event)
