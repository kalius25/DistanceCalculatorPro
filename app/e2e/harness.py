"""Headless workbook-to-result end-to-end execution harness."""

from __future__ import annotations

from pathlib import Path

from app.batch import (
    BatchProgressTracker,
    BatchSummary,
    OutputPathPolicy,
    QueueBuilder,
    ResultWriterFactory,
    RetryPolicy,
)
from app.presentation.workspace_configuration import WorkspaceConfiguration
from app.services.batch_calculation_service import BatchCalculationService
from app.services.calculation_service import CalculationService

from .fake_provider import ScriptedRouteProvider
from .models import E2ERunReport
from .report import E2EReportWriter


class HeadlessE2EHarness:
    """Run the real queue, retry, writer, resume, and summary pipeline."""

    def __init__(
        self,
        provider: ScriptedRouteProvider,
        *,
        retry_policy: RetryPolicy | None = None,
        queue_builder: QueueBuilder | None = None,
        writer_factory: ResultWriterFactory | None = None,
        report_writer: E2EReportWriter | None = None,
    ) -> None:
        self._provider = provider
        self._queue_builder = queue_builder or QueueBuilder()
        self._writer_factory = writer_factory or ResultWriterFactory()
        self._report_writer = report_writer
        calculation = CalculationService(provider)
        self._batch = BatchCalculationService(
            calculation,
            retry_policy=retry_policy,
            sleep_callback=lambda _seconds: None,
        )

    def run(
        self,
        *,
        scenario: str,
        source_path: str | Path,
        sheet_name: str,
        configuration: WorkspaceConfiguration,
        output_path: str | Path | None = None,
        resume_from_output: bool = False,
        stop_after: int | None = None,
        write_report: bool = False,
    ) -> E2ERunReport:
        source = Path(source_path)
        queue_input = (
            Path(output_path)
            if resume_from_output
            and output_path is not None
            and Path(output_path).exists()
            else source
        )
        queue = self._queue_builder.build(queue_input, sheet_name, configuration)
        output = (
            Path(output_path)
            if output_path is not None
            else OutputPathPolicy().build(source)
        )
        initial_completed = queue.terminal_count
        tracker = BatchProgressTracker(
            len(queue),
            initial_completed=initial_completed,
            initial_successful=queue.done_count,
            initial_failed=queue.failed_count + queue.invalid_count,
            initial_skipped=queue.skipped_count,
        )
        processed = 0

        def progress(_current: int, _total: int, job: object, _result: object) -> None:
            nonlocal processed
            processed += 1
            tracker.record(job)  # type: ignore[arg-type]

        def should_stop() -> bool:
            return stop_after is not None and processed >= stop_after

        writer = self._writer_factory.create(
            source,
            sheet_name,
            resume_from_output=resume_from_output,
            output_path=output,
        )
        try:
            self._batch.calculate_queue(
                queue,
                progress_callback=progress,
                should_stop=should_stop,
                result_writer=writer,
            )
        finally:
            writer.close()

        stopped = queue.pending_count > 0
        summary = BatchSummary.from_queue(
            queue,
            tracker.snapshot,
            output,
            stopped=stopped,
        )
        report = E2ERunReport(
            scenario=scenario,
            source_file=str(source),
            output_file=str(output),
            summary=summary,
            provider_requests=self._provider.requests,
            provider_batches_started=self._provider.batches_started,
            provider_batches_finished=self._provider.batches_finished,
            statuses=tuple(job.status.value for job in queue),
        )
        if write_report:
            report_writer = self._report_writer or E2EReportWriter()
            report_path = report_writer.write(report)
            report = report.with_report_file(report_path)
        return report


__all__ = ["HeadlessE2EHarness"]
