"""Background calculation worker and Qt thread coordinator."""

from __future__ import annotations

from threading import Condition

from PySide6.QtCore import QObject, QThread, Signal, Slot

from app.batch.batch_queue import BatchQueue
from app.batch.models import RouteJob
from app.batch.progress import BatchProgressTracker
from app.batch.result_writer import ResultWriterFactory
from app.batch.summary import BatchSummary, BatchSummaryWriter
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
    summary = Signal(object)
    failed_queue = Signal(object)
    finished = Signal()

    def __init__(
        self,
        job: CalculationJob,
        job_builder: CalculationJobBuilder,
        batch_service: BatchCalculationService,
        writer_factory: ResultWriterFactory | None = None,
        summary_writer: BatchSummaryWriter | None = None,
        queue_override: BatchQueue | None = None,
    ) -> None:
        super().__init__()
        self._job = job
        self._job_builder = job_builder
        self._batch_service = batch_service
        self._writer_factory = writer_factory or ResultWriterFactory()
        self._summary_writer = summary_writer or BatchSummaryWriter()
        self._queue_override = queue_override
        self._condition = Condition()
        self._paused = False
        self._stop_requested = False
        self._progress_tracker: BatchProgressTracker | None = None

    @Slot()
    def run(self) -> None:
        results: list[RouteResult] = []
        try:
            queue = self._queue_override or self._job_builder.build_queue(self._job)
            self._progress_tracker = BatchProgressTracker(
                len(queue),
                initial_completed=queue.terminal_count,
                initial_successful=queue.done_count,
                initial_failed=queue.failed_count + queue.invalid_count,
                initial_skipped=queue.skipped_count,
            )
            self.metrics.emit(self._progress_tracker.snapshot)
            with self._writer_factory.create(
                self._job.file_path,
                self._job.sheet_name,
                resume_from_output=self._queue_override is not None,
            ) as writer:
                results = self._batch_service.calculate_queue(
                    queue,
                    progress_callback=self._on_progress,
                    should_stop=self._should_stop,
                    wait_if_paused=self._wait_if_paused,
                    result_writer=writer,
                )
                stopped = self._should_stop()
                metrics = self._progress_tracker.snapshot
                summary = BatchSummary.from_queue(
                    queue,
                    metrics,
                    writer.output_path,
                    stopped=stopped,
                )
                self._summary_writer.write(summary)
            if stopped:
                self.stopped.emit(results)
            else:
                self.completed.emit(results)
            self.summary.emit(summary)
            self.failed_queue.emit(queue.failed_only())
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
    summary = Signal(object)

    def __init__(
        self,
        job_builder: CalculationJobBuilder,
        batch_service: BatchCalculationService,
        parent: QObject | None = None,
        writer_factory: ResultWriterFactory | None = None,
        summary_writer: BatchSummaryWriter | None = None,
    ) -> None:
        super().__init__(parent)
        self._job_builder = job_builder
        self._batch_service = batch_service
        self._writer_factory = writer_factory or ResultWriterFactory()
        self._summary_writer = summary_writer or BatchSummaryWriter()
        self._thread: QThread | None = None
        self._worker: CalculationWorker | None = None
        self._last_job: CalculationJob | None = None
        self._failed_queue: BatchQueue | None = None

    @property
    def is_running(self) -> bool:
        return self._thread is not None

    def start(self, job: CalculationJob) -> bool:
        if self.is_running:
            return False
        self._last_job = job
        return self._start_worker(job, None)

    def retry_failed(self) -> bool:
        if (
            self.is_running
            or self._last_job is None
            or self._failed_queue is None
            or self._failed_queue.pending_count == 0
        ):
            return False
        return self._start_worker(self._last_job, self._failed_queue)

    def _start_worker(
        self,
        job: CalculationJob,
        queue_override: BatchQueue | None,
    ) -> bool:
        thread = QThread(self)
        worker = CalculationWorker(
            job,
            self._job_builder,
            self._batch_service,
            self._writer_factory,
            self._summary_writer,
            queue_override,
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.progress.connect(self.progress.emit)
        worker.metrics.connect(self.metrics.emit)
        worker.completed.connect(self.completed.emit)
        worker.stopped.connect(self.stopped.emit)
        worker.failed.connect(self.failed.emit)
        worker.summary.connect(self.summary.emit)
        worker.failed_queue.connect(self._store_failed_queue)
        worker.finished.connect(thread.quit)
        worker.finished.connect(worker.deleteLater)
        thread.finished.connect(self._clear_worker)
        thread.finished.connect(thread.deleteLater)
        self._thread = thread
        self._worker = worker
        thread.start()
        return True

    @Slot(object)
    def _store_failed_queue(self, queue: object) -> None:
        self._failed_queue = queue if isinstance(queue, BatchQueue) else None

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
