from __future__ import annotations

from unittest.mock import MagicMock, patch

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
    builder.build_requests.return_value = [request]
    batch = MagicMock()

    def calculate(
        requests: object,
        progress_callback: object,
        **kwargs: object,
    ) -> list[RouteResult]:
        assert list(requests) == [request]  # type: ignore[arg-type]
        progress_callback(1, 1, request, result)  # type: ignore[operator]
        return [result]

    batch.calculate.side_effect = calculate
    worker = CalculationWorker(job, builder, batch)

    with (
        qtbot.waitSignal(worker.progress),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.completed),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.finished),  # type: ignore[attr-defined]
    ):
        worker.run()


def test_worker_stopped_failed_and_control_methods(qtbot: object) -> None:
    job = MagicMock(spec=CalculationJob)
    builder = MagicMock()
    builder.build_requests.return_value = []
    batch = MagicMock()
    worker = CalculationWorker(job, builder, batch)
    worker.request_stop()
    batch.calculate.return_value = []

    with (
        qtbot.waitSignal(worker.stopped),  # type: ignore[attr-defined]
        qtbot.waitSignal(worker.finished),  # type: ignore[attr-defined]
    ):
        worker.run()

    worker = CalculationWorker(job, builder, batch)
    builder.build_requests.side_effect = ValueError("bad job")
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
    result = RouteResult(True, request, "Google")
    with qtbot.waitSignal(  # type: ignore[attr-defined]
        worker.progress,
        check_params_cb=lambda *values: values == (1, 2, request, result),
    ):
        worker._on_progress(1, 2, request, result)


def test_coordinator_starts_controls_and_clears_worker() -> None:
    coordinator = CalculationExecutionCoordinator(MagicMock(), MagicMock())
    thread = MagicMock()
    worker = MagicMock()
    worker.progress = MagicMock()
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
