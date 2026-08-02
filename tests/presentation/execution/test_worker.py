from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.batch import BatchQueue, RouteJob, RouteJobStatus
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.presentation.execution.job import CalculationJob
from app.presentation.execution.worker import (
    CalculationExecutionCoordinator,
    CalculationWorker,
)


def test_worker_completes_and_relays_progress(qtbot: object) -> None:
    job = MagicMock(spec=CalculationJob)
    request = RouteRequest("A", "B")
    result = RouteResult(True, request, "Google")
    builder = MagicMock()
    route_job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([route_job])
    builder.build_queue.return_value = queue
    batch = MagicMock()

    def calculate_queue(
        received_queue: object,
        progress_callback: object,
        **kwargs: object,
    ) -> list[RouteResult]:
        assert received_queue is queue
        progress_callback(1, 1, route_job, result)  # type: ignore[operator]
        return [result]

    batch.calculate_queue.side_effect = calculate_queue
    writer = MagicMock()
    writer.__enter__.return_value = writer
    writer_factory = MagicMock()
    writer_factory.create.return_value = writer
    worker = CalculationWorker(job, builder, batch, writer_factory)

    with (
        qtbot.waitSignal(worker.progress),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.metrics),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.completed),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.finished),  # type: ignore[attr-defined]
    ):
        worker.run()


def test_worker_stopped_failed_and_control_methods(qtbot: object) -> None:
    job = MagicMock(spec=CalculationJob)
    builder = MagicMock()
    builder.build_queue.return_value = BatchQueue()
    batch = MagicMock()
    writer = MagicMock()
    writer.__enter__.return_value = writer
    writer_factory = MagicMock()
    writer_factory.create.return_value = writer
    worker = CalculationWorker(job, builder, batch, writer_factory)
    worker.request_stop()
    batch.calculate_queue.return_value = []

    with (
        qtbot.waitSignal(worker.stopped),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.finished),  # type: ignore[attr-defined]
    ):
        worker.run()

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


def test_worker_progress_helper_emits_signal(qtbot: object) -> None:
    worker = CalculationWorker(MagicMock(), MagicMock(), MagicMock())
    request = RouteRequest("A", "B")
    route_job = RouteJob(2, "A", "B", "Distance")
    result = RouteResult(True, request, "Google")
    with qtbot.waitSignal(worker.progress):  # type: ignore[attr-defined]
        worker._on_progress(1, 2, route_job, result)

    route_job.status = RouteJobStatus.DONE
    from app.batch.progress import BatchProgressTracker

    worker._progress_tracker = BatchProgressTracker(2, clock=lambda: 1.0)
    worker.request_pause()
    worker.request_resume()
    with (
        qtbot.waitSignal(  # type: ignore[attr-defined]
            worker.progress,
            check_params_cb=lambda *values: values == (1, 2, route_job, result),
        ),
        qtbot.waitSignal(worker.metrics),  # type: ignore[attr-defined]
    ):
        worker._on_progress(1, 2, route_job, result)


def test_coordinator_starts_controls_and_clears_worker() -> None:
    coordinator = CalculationExecutionCoordinator(MagicMock(), MagicMock())
    thread = MagicMock()
    worker = MagicMock()
    worker.progress = MagicMock()
    worker.metrics = MagicMock()
    worker.completed = MagicMock()
    worker.stopped = MagicMock()
    worker.failed = MagicMock()
    worker.finished = MagicMock()
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
        assert coordinator.start(MagicMock())
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
    coordinator.pause()
    coordinator.resume()
    coordinator.stop()
