"""Background calculation worker and Qt thread coordinator."""

from __future__ import annotations

from threading import Condition

from PySide6.QtCore import QObject, QThread, Signal, Slot

from app.batch.models import RouteJob
from app.batch.progress import BatchProgressTracker
from app.batch.result_writer import ResultWriterFactory
from app.models.route_result import RouteResult
from app.services.batch_calculation_service import BatchCalculationService

from .job import CalculationJob, CalculationJobBuilder


class CalculationWorker(QObject):
    """Run one calculation job outside the GUI thread."""

    progress = Signal(int, int, object, object)
    metrics = Signal(object)
    completed = Signal(object)
    stopped = Signal(object)
    failed = Signal(str)
    finished = Signal()

    def __init__(
        self,
        job: CalculationJob,
        job_builder: CalculationJobBuilder,
        batch_service: BatchCalculationService,
        writer_factory: ResultWriterFactory | None = None,
    ) -> None:
        super().__init__()
        self._job = job
        self._job_builder = job_builder
        self._batch_service = batch_service
        self._writer_factory = writer_factory or ResultWriterFactory()
        self._condition = Condition()
        self._paused = False
        self._stop_requested = False
        self._progress_tracker: BatchProgressTracker | None = None

    @Slot()
    def run(self) -> None:
        results: list[RouteResult] = []
        try:
            queue = self._job_builder.build_queue(self._job)
            self._progress_tracker = BatchProgressTracker(queue.pending_count)
            with self._writer_factory.create(
                self._job.file_path,
                self._job.sheet_name,
            ) as writer:
                results = self._batch_service.calculate_queue(
                    queue,
                    progress_callback=self._on_progress,
                    should_stop=self._should_stop,
                    wait_if_paused=self._wait_if_paused,
                    result_writer=writer,
                )
            if self._should_stop():
                self.stopped.emit(results)
            else:
                self.completed.emit(results)
        except Exception as error:  # presentation boundary
            self.failed.emit(str(error))
        finally:
            self.finished.emit()

    def request_pause(self) -> None:
        with self._condition:
            self._paused = True
            if self._progress_tracker is not None:
                self._progress_tracker.pause()

    def request_resume(self) -> None:
        with self._condition:
            self._paused = False
            if self._progress_tracker is not None:
                self._progress_tracker.resume()
            self._condition.notify_all()

    def request_stop(self) -> None:
        with self._condition:
            self._stop_requested = True
            self._paused = False
            self._condition.notify_all()

    def _should_stop(self) -> bool:
        with self._condition:
            return self._stop_requested

    def _wait_if_paused(self) -> None:
        with self._condition:
            while self._paused and not self._stop_requested:
                self._condition.wait()

    def _on_progress(
        self,
        current: int,
        total: int,
        job: RouteJob,
        result: RouteResult,
    ) -> None:
        self.progress.emit(current, total, job, result)
        if self._progress_tracker is not None:
            self.metrics.emit(self._progress_tracker.record(job))


class CalculationExecutionCoordinator(QObject):
    """Own the worker thread and relay execution events to the UI."""

    progress = Signal(int, int, object, object)
    metrics = Signal(object)
    completed = Signal(object)
    stopped = Signal(object)
    failed = Signal(str)

    def __init__(
        self,
        job_builder: CalculationJobBuilder,
        batch_service: BatchCalculationService,
        parent: QObject | None = None,
        writer_factory: ResultWriterFactory | None = None,
    ) -> None:
        super().__init__(parent)
        self._job_builder = job_builder
        self._batch_service = batch_service
        self._writer_factory = writer_factory or ResultWriterFactory()
        self._thread: QThread | None = None
        self._worker: CalculationWorker | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None

    def start(self, job: CalculationJob) -> bool:
        if self.is_running:
            return False

        thread = QThread(self)
        worker = CalculationWorker(
            job,
            self._job_builder,
            self._batch_service,
            self._writer_factory,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.progress.emit)
        worker.metrics.connect(self.metrics.emit)
        worker.completed.connect(self.completed.emit)
        worker.stopped.connect(self.stopped.emit)
        worker.failed.connect(self.failed.emit)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._clear_worker)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        self._worker = worker
        thread.start()
        return True

    def pause(self) -> None:
        if self._worker is not None:
            self._worker.request_pause()

    def resume(self) -> None:
        if self._worker is not None:
            self._worker.request_resume()

    def stop(self) -> None:
        if self._worker is not None:
            self._worker.request_stop()

    @Slot()
    def _clear_worker(self) -> None:
        self._worker = None
        self._thread = None
