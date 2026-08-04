"""Deterministic execution coordinator used by GUI smoke tests."""

from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, QTimer, Signal

from app.batch.progress import ProgressSnapshot
from app.batch.summary import BatchSummary
from app.presentation.execution.job import CalculationJob


class ScriptedGuiCoordinator(QObject):
    """Emit a successful batch lifecycle without browser or network access."""

    progress = Signal(int, int, object, object)
    metrics = Signal(object)
    completed = Signal(object)
    stopped = Signal(object)
    failed = Signal(str)
    output_write_failed = Signal(object)
    summary = Signal(object)

    def __init__(
        self,
        *,
        result_factory: Callable[[CalculationJob], list[object]] | None = None,
    ) -> None:
        super().__init__()
        self._result_factory = result_factory or (lambda _job: [object()])
        self._running = False
        self.last_job: CalculationJob | None = None
        self.start_calls = 0
        self.shutdown_calls = 0

    @property
    def is_running(self) -> bool:
        return self._running

    def start(self, job: CalculationJob) -> bool:
        if self._running:
            return False
        self._running = True
        self.last_job = job
        self.start_calls += 1
        QTimer.singleShot(0, lambda: self._complete(job))
        return True

    def _complete(self, job: CalculationJob) -> None:
        results = self._result_factory(job)
        total = len(results)
        if total:
            self.progress.emit(total, total, object(), results[-1])
        metrics = ProgressSnapshot(
            total=total,
            completed=total,
            successful=total,
            failed=0,
            skipped=0,
            remaining=0,
            elapsed_seconds=0.1,
            average_seconds_per_item=(0.1 / total if total else 0.0),
            items_per_minute=float(total * 600),
            eta_seconds=0.0,
            percent_complete=100.0 if total else 100.0,
        )
        summary = BatchSummary(
            total=total,
            completed=total,
            successful=total,
            failed=0,
            skipped=0,
            invalid=0,
            resumed=0,
            retry_count=0,
            elapsed_seconds=0.1,
            items_per_minute=float(total * 600),
            output_file=job.output_path or "",
        )
        self.metrics.emit(metrics)
        self.summary.emit(summary)
        self._running = False
        self.completed.emit(results)

    def pause(self) -> None:
        return None

    def resume(self) -> None:
        return None

    def stop(self) -> None:
        if self._running:
            self._running = False
            self.stopped.emit([])

    def retry_failed(self) -> bool:
        return False

    def retry_with_output(self, _output_path: str) -> bool:
        return False

    def shutdown(self, _timeout_ms: int = 5_000) -> bool:
        self.shutdown_calls += 1
        self._running = False
        return True


__all__ = ["ScriptedGuiCoordinator"]
