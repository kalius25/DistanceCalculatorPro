from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.gui_smoke import (
    GuiSmokeHarness,
    GuiSmokeReportWriter,
    GuiSmokeResult,
    ScriptedGuiCoordinator,
)
from app.presentation.app_metadata import AppMetadata
from app.presentation.main_window import MainWindow
from app.presentation.models.execution_state import ExecutionState
from app.presentation.preflight import PreflightResult


@pytest.fixture
def smoke_window(
    qtbot: object,
    qapp: QApplication,
    tmp_path: Path,
) -> MainWindow:
    settings = MagicMock()
    settings.toolbar_visible.return_value = True
    settings.recent_files.return_value = []
    settings.window_geometry.return_value = None
    settings.window_state.return_value = None
    settings.workspace_panels_visible.return_value = True
    settings.workspace_splitter_state.return_value = None
    settings.debug_enabled.return_value = False
    settings.trace_browser.return_value = False
    settings.parser_diagnostics.return_value = False
    settings.save_html.return_value = False
    settings.save_screenshot.return_value = False
    settings.save_json.return_value = False

    theme = MagicMock()
    theme.current_theme = "light"

    coordinator = ScriptedGuiCoordinator()
    preflight = MagicMock()
    output = tmp_path / "routes.result.csv"
    preflight.validate.return_value = PreflightResult(
        output_path=output,
        estimated_job_count=1,
        estimated_output_bytes=256,
        required_free_bytes=512,
        available_bytes=1_024,
    )

    with patch(
        "app.presentation.main_window.qta.icon",
        return_value=QIcon(),
    ):
        window = MainWindow(
            application=qapp,
            metadata=AppMetadata(),
            theme_manager=theme,
            settings_manager=settings,
            workbook_inspector=MagicMock(),
            execution_coordinator=coordinator,
            preflight_validator=preflight,
        )
    qtbot.addWidget(window)  # type: ignore[attr-defined]
    window._output_path_policy = MagicMock()
    window._output_path_policy.build.return_value = output
    window.show()
    qapp.processEvents()
    return window


@pytest.mark.gui_smoke
@pytest.mark.smoke
def test_gui_smoke_happy_path(
    smoke_window: MainWindow,
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    source = tmp_path / "routes.csv"
    source.write_text(
        "Origin,Destination,Distance,Duration\nA,B,,\n",
        encoding="utf-8",
    )

    harness = GuiSmokeHarness(qapp, smoke_window)
    harness.prepare_workbook(source)

    assert smoke_window._home_page.workspace_ready

    result = harness.run_happy_path()

    assert result.passed
    assert result.final_state == "IDLE"
    assert result.progress_events == 1
    assert result.summary_events == 1
    assert result.completed_events == 1
    assert result.final_status == "Calculation completed · 1 results"
    assert result.output_path.endswith("routes.result.csv")


@pytest.mark.gui_smoke
def test_scripted_gui_coordinator_rejects_parallel_start(
    qapp: QApplication,
) -> None:
    coordinator = ScriptedGuiCoordinator()
    job = MagicMock()

    assert coordinator.start(job)
    assert not coordinator.start(job)

    qapp.processEvents()

    assert coordinator.start_calls == 1
    assert not coordinator.is_running
    assert coordinator.shutdown()
    assert coordinator.shutdown_calls == 1


@pytest.mark.gui_smoke
def test_gui_smoke_result_and_report(tmp_path: Path) -> None:
    result = GuiSmokeResult(
        scenario="gui_happy_path",
        passed=True,
        final_status="Calculation completed · 1 results",
        final_state="IDLE",
        progress_events=1,
        summary_events=1,
        completed_events=1,
        output_path="routes.result.csv",
    )

    output = GuiSmokeReportWriter().write(
        result,
        tmp_path / "reports" / "gui-smoke.json",
    )
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload == result.to_dict()


@pytest.mark.gui_smoke
def test_scripted_gui_coordinator_supports_empty_results_and_controls(
    qapp: QApplication,
) -> None:
    coordinator = ScriptedGuiCoordinator(result_factory=lambda _job: [])
    job = MagicMock()
    job.output_path = None

    completed: list[object] = []
    progress: list[object] = []
    coordinator.completed.connect(completed.append)
    coordinator.progress.connect(lambda *_args: progress.append(object()))

    assert coordinator.start(job)
    coordinator.pause()
    coordinator.resume()

    qapp.processEvents()

    assert completed == [[]]
    assert progress == []
    assert not coordinator.retry_failed()
    assert not coordinator.retry_with_output("other.csv")
    coordinator.stop()
    assert not coordinator.is_running


@pytest.mark.gui_smoke
def test_scripted_gui_coordinator_stop_emits_stopped(
    qtbot: object,
) -> None:
    coordinator = ScriptedGuiCoordinator()
    job = MagicMock()

    with qtbot.waitSignal(coordinator.stopped):  # type: ignore[attr-defined]
        assert coordinator.start(job)
        coordinator.stop()

    assert not coordinator.is_running


@pytest.mark.gui_smoke
def test_gui_smoke_harness_without_coordinator_reports_failure(
    smoke_window: MainWindow,
    qapp: QApplication,
    tmp_path: Path,
) -> None:
    source = tmp_path / "routes.csv"
    source.write_text(
        "Origin,Destination,Distance,Duration\nA,B,,\n",
        encoding="utf-8",
    )
    harness = GuiSmokeHarness(qapp, smoke_window)
    harness.prepare_workbook(source)

    original_coordinator = smoke_window._execution_coordinator
    try:
        smoke_window._execution_coordinator = None
        result = harness.run_happy_path()
    finally:
        smoke_window._execution_coordinator = original_coordinator
        smoke_window._set_execution_state(ExecutionState.IDLE)

    assert not result.passed
    assert result.output_path == ""
    assert result.completed_events == 0
