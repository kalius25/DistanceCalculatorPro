"""Qt GUI smoke harness for deterministic happy-path verification."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.presentation.main_window import MainWindow
from app.presentation.models.execution_state import ExecutionState
from app.workbooks.models import WorkbookInfo, WorksheetInfo

from .models import GuiSmokeResult


class GuiSmokeHarness:
    """Drive a prepared MainWindow through the basic successful workflow."""

    def __init__(self, application: QApplication, window: MainWindow) -> None:
        self._application = application
        self._window = window

    def prepare_workbook(self, file_path: str | Path) -> None:
        path = Path(file_path)
        info = WorkbookInfo(
            file_path=str(path),
            file_name=path.name,
            file_type=path.suffix.lstrip(".").upper(),
            file_size_bytes=path.stat().st_size,
            modified_at=datetime.fromtimestamp(path.stat().st_mtime),
            worksheets=(
                WorksheetInfo(
                    "Routes",
                    2,
                    4,
                    ("Origin", "Destination", "Distance", "Duration"),
                    (("A", "B", "", ""),),
                ),
            ),
        )
        self._window._home_page.set_selected_file(str(path))
        self._window._home_page.set_inspection(info)
        self._application.processEvents()

    def run_happy_path(self) -> GuiSmokeResult:
        progress_events = 0
        summary_events = 0
        completed_events = 0

        def on_progress(*_args: object) -> None:
            nonlocal progress_events
            progress_events += 1

        def on_summary(_summary: object) -> None:
            nonlocal summary_events
            summary_events += 1

        def on_completed(_results: object) -> None:
            nonlocal completed_events
            completed_events += 1

        self._window.calculation_progress.connect(on_progress)
        self._window.calculation_summary.connect(on_summary)
        self._window.calculation_completed.connect(on_completed)

        error = ""
        try:
            self._window._action_start.trigger()
            self._application.processEvents()
            self._application.processEvents()
        except Exception as caught:  # pragma: no cover - reported to caller
            error = str(caught)

        coordinator = self._window._execution_coordinator
        output_path = ""
        last_job = (
            getattr(coordinator, "last_job", None) if coordinator is not None else None
        )
        if last_job is not None:
            output_path = last_job.output_path or ""

        passed = (
            not error
            and self._window.execution_state is ExecutionState.IDLE
            and completed_events == 1
            and summary_events == 1
        )
        return GuiSmokeResult(
            scenario="gui_happy_path",
            passed=passed,
            final_status=self._window._status_label.text(),
            final_state=self._window.execution_state.name,
            progress_events=progress_events,
            summary_events=summary_events,
            completed_events=completed_events,
            output_path=output_path,
            error=error,
        )


__all__ = ["GuiSmokeHarness"]
