from __future__ import annotations

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, call, patch

import pytest
from PySide6.QtCore import QByteArray
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QApplication, QFileDialog, QMessageBox

from app.presentation.app_metadata import AppMetadata
from app.presentation.main_window import MainWindow
from app.presentation.models.execution_state import ExecutionState
from app.workbooks.models import WorkbookInfo, WorksheetInfo


@pytest.fixture
def metadata() -> AppMetadata:
    return AppMetadata()


@pytest.fixture
def settings_manager() -> MagicMock:
    manager = MagicMock()
    manager.toolbar_visible.return_value = True
    manager.recent_files.return_value = []
    manager.window_geometry.return_value = None
    manager.window_state.return_value = None
    return manager


@pytest.fixture
def theme_manager() -> MagicMock:
    manager = MagicMock()
    manager.current_theme = "light"
    return manager


@pytest.fixture
def workbook_inspector(tmp_path: Path) -> MagicMock:
    inspector = MagicMock()
    inspector.inspect.side_effect = lambda file_path: WorkbookInfo(
        file_path=file_path,
        file_name=Path(file_path).name,
        file_type=Path(file_path).suffix.lstrip(".").upper(),
        file_size_bytes=Path(file_path).stat().st_size,
        modified_at=datetime.fromtimestamp(
            Path(file_path).stat().st_mtime
        ),
        worksheets=(WorksheetInfo("Sheet1", 1, 1, ("Header",)),),
    )
    return inspector


@pytest.fixture
def window(
    qtbot: object,
    qapp: QApplication,
    metadata: AppMetadata,
    theme_manager: MagicMock,
    settings_manager: MagicMock,
    workbook_inspector: MagicMock,
) -> MainWindow:
    with patch(
        "app.presentation.main_window.qta.icon",
        return_value=QIcon(),
    ):
        result = MainWindow(
            application=qapp,
            metadata=metadata,
            theme_manager=theme_manager,
            settings_manager=settings_manager,
            workbook_inspector=workbook_inspector,
        )
    qtbot.addWidget(result)  # type: ignore[attr-defined]
    result.show()
    qapp.processEvents()
    return result


def test_initial_shell_structure_and_state(
    window: MainWindow,
    metadata: AppMetadata,
) -> None:
    assert window.windowTitle() == metadata.name
    assert window.minimumWidth() == 1100
    assert window.minimumHeight() == 700
    assert window._content_stack.count() == 4
    assert window._content_stack.currentIndex() == window.HOME_PAGE_INDEX
    assert window._home_page.selected_file is None
    assert window._status_label.text() == "Ready · Home"
    assert window._provider_label.text() == "Provider: -"
    assert window._theme_label.text() == "Theme: Light"
    assert window._version_label.text() == (
        f"{metadata.name} v{metadata.version}"
    )
    assert window._action_light_theme.isChecked()
    assert not window._action_dark_theme.isChecked()
    assert window._toolbar.isVisible()
    assert [action.text() for action in window.menuBar().actions()] == [
        "&File",
        "&View",
        "&Help",
    ]


def test_initial_state_restores_saved_geometry_and_window_state(
    qtbot: object,
    qapp: QApplication,
    metadata: AppMetadata,
    theme_manager: MagicMock,
    settings_manager: MagicMock,
) -> None:
    geometry = QByteArray(b"geometry")
    state = QByteArray(b"state")
    settings_manager.window_geometry.return_value = geometry
    settings_manager.window_state.return_value = state

    with (
        patch("app.presentation.main_window.qta.icon", return_value=QIcon()),
        patch.object(
            MainWindow,
            "restoreGeometry",
            return_value=True,
        ) as restore_geometry,
        patch.object(MainWindow, "restoreState", return_value=True) as restore_state,
    ):
        result = MainWindow(
            application=qapp,
            metadata=metadata,
            theme_manager=theme_manager,
            settings_manager=settings_manager,
        )
    qtbot.addWidget(result)  # type: ignore[attr-defined]

    restore_geometry.assert_called_once_with(geometry)
    restore_state.assert_called_once_with(state)


def test_navigation_panel_and_navigation_actions_change_pages(
    window: MainWindow,
) -> None:
    window._navigation.setCurrentRow(window.HISTORY_PAGE_INDEX)
    assert window._content_stack.currentIndex() == window.HISTORY_PAGE_INDEX
    assert window._status_label.text() == "Ready · History"

    window._action_settings_page.trigger()
    assert window._content_stack.currentIndex() == window.SETTINGS_PAGE_INDEX
    assert window._status_label.text() == "Ready · Settings"

    window._action_about_page.trigger()
    assert window._content_stack.currentIndex() == window.ABOUT_PAGE_INDEX

    window._action_home.trigger()
    assert window._content_stack.currentIndex() == window.HOME_PAGE_INDEX


def test_toolbar_settings_action_selects_settings_page(
    window: MainWindow,
) -> None:
    window._action_settings.trigger()

    assert window._navigation.currentRow() == window.SETTINGS_PAGE_INDEX
    assert window._content_stack.currentIndex() == window.SETTINGS_PAGE_INDEX


def test_invalid_page_index_does_not_replace_status_text(
    window: MainWindow,
) -> None:
    window._status_label.setText("unchanged")

    window._on_current_page_changed(-1)
    window._on_current_page_changed(len(window.PAGE_NAMES))

    assert window._status_label.text() == "unchanged"


def test_show_action_page_ignores_non_action_sender(
    window: MainWindow,
) -> None:
    original_row = window._navigation.currentRow()

    with patch.object(window, "sender", return_value=None):
        window._show_action_page()

    assert window._navigation.currentRow() == original_row


def test_theme_actions_apply_and_persist_theme(
    window: MainWindow,
    qapp: QApplication,
    theme_manager: MagicMock,
    settings_manager: MagicMock,
) -> None:
    with patch.object(window, "_update_action_icons") as update_icons:
        window._action_dark_theme.trigger()

        theme_manager.apply_theme.assert_called_once_with(qapp, "dark")
        settings_manager.set_theme_name.assert_called_once_with("dark")
        assert window._theme_label.text() == "Theme: Dark"
        assert window._action_dark_theme.isChecked()
        assert not window._action_light_theme.isChecked()
        update_icons.assert_called_once_with("dark")

        window._action_light_theme.trigger()

    assert theme_manager.apply_theme.call_args_list == [
        call(qapp, "dark"),
        call(qapp, "light"),
    ]
    assert settings_manager.set_theme_name.call_args_list == [
        call("dark"),
        call("light"),
    ]


def test_action_icons_use_theme_specific_and_disabled_colors(
    window: MainWindow,
) -> None:
    with patch(
        "app.presentation.main_window.qta.icon",
        return_value=QIcon(),
    ) as icon_factory:
        window._update_action_icons("light")
        light_calls = icon_factory.call_args_list
        icon_factory.reset_mock()

        window._update_action_icons("dark")
        dark_calls = icon_factory.call_args_list

    assert len(light_calls) == 5
    assert len(dark_calls) == 5
    assert all(
        item.kwargs == {
            "color": window.LIGHT_ICON_COLOR,
            "color_disabled": window.DISABLED_ICON_COLOR,
        }
        for item in light_calls
    )
    assert all(
        item.kwargs == {
            "color": window.DARK_ICON_COLOR,
            "color_disabled": window.DISABLED_ICON_COLOR,
        }
        for item in dark_calls
    )


def test_empty_recent_files_menu_contains_disabled_placeholder(
    window: MainWindow,
) -> None:
    actions = window._recent_files_menu.actions()

    assert len(actions) == 1
    assert actions[0].text() == "No recent files"
    assert not actions[0].isEnabled()


def test_recent_files_menu_builds_actions_and_selects_workbook(
    window: MainWindow,
    settings_manager: MagicMock,
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.xlsx"
    second = tmp_path / "second.xlsx"
    first.touch()
    second.touch()
    first_path = str(first)
    second_path = str(second)
    settings_manager.recent_files.return_value = [first_path, second_path]

    window._update_recent_files_menu()
    actions = window._recent_files_menu.actions()

    assert actions[0].text() == "first.xlsx"
    assert actions[0].toolTip() == first_path
    assert actions[0].data() == first_path
    assert actions[1].text() == "second.xlsx"
    assert actions[-1].text() == "Clear Recent Files"

    actions[0].trigger()

    assert window._home_page.selected_file == first_path
    settings_manager.add_recent_file.assert_called_once_with(first_path)
    assert window._status_label.text() == "Ready · first.xlsx"


def test_recent_file_handler_ignores_non_action_sender(
    window: MainWindow,
) -> None:
    with (
        patch.object(window, "sender", return_value=None),
        patch.object(window, "_select_workbook") as select_workbook,
    ):
        window._show_recent_file_placeholder()

    select_workbook.assert_not_called()


def test_clear_recent_files_updates_manager_and_menu(
    window: MainWindow,
    settings_manager: MagicMock,
) -> None:
    settings_manager.recent_files.side_effect = [
        ["C:/data/file.xlsx"],
        [],
    ]
    window._update_recent_files_menu()

    window._recent_files_menu.actions()[-1].trigger()

    settings_manager.clear_recent_files.assert_called_once_with()
    actions = window._recent_files_menu.actions()
    assert len(actions) == 1
    assert actions[0].text() == "No recent files"
    assert not actions[0].isEnabled()


def _make_workspace_ready(window: MainWindow) -> object:
    window._home_page.set_inspection(
        WorkbookInfo(
            file_path="routes.xlsx",
            file_name="routes.xlsx",
            file_type="XLSX",
            file_size_bytes=100,
            modified_at=datetime(2026, 7, 31, 16, 0),
            worksheets=(
                WorksheetInfo(
                    "Routes",
                    25,
                    3,
                    ("Origin", "Destination", "Distance"),
                ),
            ),
        )
    )
    configuration = window._home_page.workspace_configuration
    assert configuration is not None
    return configuration


def test_execution_actions_start_pause_resume_and_stop(
    window: MainWindow,
    qtbot: object,
) -> None:
    configuration = _make_workspace_ready(window)
    assert window._action_start.isEnabled()
    assert not window._action_pause.isEnabled()
    assert not window._action_stop.isEnabled()

    with qtbot.waitSignal(  # type: ignore[attr-defined]
        window.calculation_requested,
        check_params_cb=lambda emitted: emitted == configuration,
    ):
        window._action_start.trigger()

    assert window.execution_state is ExecutionState.RUNNING
    assert not window._action_start.isEnabled()
    assert window._action_pause.isEnabled()
    assert window._action_stop.isEnabled()
    assert window._home_page.workspace_locked
    assert not window._home_page._mapping_frame.isEnabled()
    assert window._status_label.text() == "Calculation running"

    with qtbot.waitSignal(  # type: ignore[attr-defined]
        window.calculation_pause_requested
    ):
        window._action_pause.trigger()

    assert window.execution_state is ExecutionState.PAUSED
    assert window._action_pause.text() == "Resume"
    assert window._status_label.text() == "Calculation paused"

    with qtbot.waitSignal(  # type: ignore[attr-defined]
        window.calculation_resume_requested
    ):
        window._action_pause.trigger()

    assert window.execution_state is ExecutionState.RUNNING
    assert window._action_pause.text() == "Pause"

    with qtbot.waitSignal(  # type: ignore[attr-defined]
        window.calculation_stop_requested
    ):
        window._action_stop.trigger()

    assert window.execution_state is ExecutionState.IDLE
    assert window._action_start.isEnabled()
    assert not window._action_pause.isEnabled()
    assert not window._action_stop.isEnabled()
    assert not window._home_page.workspace_locked
    assert window._home_page._mapping_frame.isEnabled()
    assert window._status_label.text() == "Ready to calculate"


def test_execution_actions_ignore_invalid_transitions(
    window: MainWindow,
    qtbot: object,
) -> None:
    assert window.execution_state is ExecutionState.IDLE
    assert not window._action_start.isEnabled()

    with (
        qtbot.assertNotEmitted(  # type: ignore[attr-defined]
            window.calculation_requested
        ),
        qtbot.assertNotEmitted(  # type: ignore[attr-defined]
            window.calculation_pause_requested
        ),
        qtbot.assertNotEmitted(  # type: ignore[attr-defined]
            window.calculation_resume_requested
        ),
        qtbot.assertNotEmitted(  # type: ignore[attr-defined]
            window.calculation_stop_requested
        ),
    ):
        window._start_calculation()
        window._toggle_pause()
        window._stop_calculation()
        window._set_execution_state(ExecutionState.IDLE)


def test_open_action_browses_and_selects_file(
    window: MainWindow,
    settings_manager: MagicMock,
    tmp_path: Path,
) -> None:
    workbook = tmp_path / "routes.xlsx"
    workbook.touch()
    settings_manager.recent_files.return_value = [str(workbook)]

    with patch.object(
        QFileDialog,
        "getOpenFileName",
        return_value=(str(workbook), "Excel workbooks"),
    ) as get_file_name:
        window._action_open.trigger()

    get_file_name.assert_called_once()
    assert window._home_page.selected_file == str(workbook)
    settings_manager.add_recent_file.assert_called_once_with(str(workbook))
    assert window._status_label.text() == "Ready · routes.xlsx"


def test_cancelled_browse_does_not_change_workspace(
    window: MainWindow,
    settings_manager: MagicMock,
) -> None:
    with patch.object(
        QFileDialog,
        "getOpenFileName",
        return_value=("", ""),
    ):
        window._browse_for_workbook()

    assert window._home_page.selected_file is None
    settings_manager.add_recent_file.assert_not_called()


def test_select_workbook_rejects_missing_file(
    window: MainWindow,
    settings_manager: MagicMock,
    tmp_path: Path,
) -> None:
    missing_file = tmp_path / "missing.xlsx"

    with patch.object(QMessageBox, "warning") as warning:
        window._select_workbook(str(missing_file))

    warning.assert_called_once_with(
        window,
        "Workbook unavailable",
        f"The selected workbook does not exist.\n\n{missing_file}",
    )
    settings_manager.add_recent_file.assert_not_called()


def test_select_workbook_rejects_unsupported_file(
    window: MainWindow,
    settings_manager: MagicMock,
    tmp_path: Path,
) -> None:
    unsupported_file = tmp_path / "routes.txt"
    unsupported_file.touch()

    with patch.object(QMessageBox, "warning") as warning:
        window._select_workbook(str(unsupported_file))

    warning.assert_called_once_with(
        window,
        "Unsupported workbook",
        "Select an .xlsx, .xlsm or .csv file.",
    )
    settings_manager.add_recent_file.assert_not_called()


def test_workspace_signals_are_connected_to_main_window(
    window: MainWindow,
    tmp_path: Path,
) -> None:
    workbook = tmp_path / "routes.csv"
    workbook.touch()

    with patch.object(window, "_browse_for_workbook") as browse:
        window._home_page.browse_requested.emit()

    browse.assert_called_once_with()

    window._home_page.file_selected.emit(str(workbook))

    assert window._home_page.selected_file == str(workbook)


def test_about_action_executes_dialog(
    window: MainWindow,
    metadata: AppMetadata,
) -> None:
    dialog = MagicMock()
    with patch(
        "app.presentation.main_window.AboutDialog",
        return_value=dialog,
    ) as dialog_type:
        window._action_about.trigger()

    dialog_type.assert_called_once_with(metadata, window)
    dialog.exec.assert_called_once_with()


def test_toolbar_visibility_is_persisted_when_signal_changes(
    window: MainWindow,
    settings_manager: MagicMock,
) -> None:
    settings_manager.set_toolbar_visible.reset_mock()

    window._toolbar.setVisible(False)

    settings_manager.set_toolbar_visible.assert_called_with(False)


def test_close_event_persists_window_state(
    window: MainWindow,
    settings_manager: MagicMock,
) -> None:
    event = QCloseEvent()
    settings_manager.set_window_geometry.reset_mock()
    settings_manager.set_window_state.reset_mock()
    settings_manager.set_toolbar_visible.reset_mock()

    window.closeEvent(event)

    settings_manager.set_window_geometry.assert_called_once()
    settings_manager.set_window_state.assert_called_once()
    settings_manager.set_toolbar_visible.assert_called_once_with(
        window._toolbar.isVisible()
    )
    assert event.isAccepted()


def test_select_workbook_handles_inspection_failure(
    window: MainWindow,
    settings_manager: MagicMock,
    workbook_inspector: MagicMock,
    tmp_path: Path,
) -> None:
    workbook = tmp_path / "broken.xlsx"
    workbook.touch()
    workbook_inspector.inspect.side_effect = ValueError("Invalid workbook")

    with patch.object(QMessageBox, "critical") as critical:
        window._select_workbook(str(workbook))

    assert window._home_page.selected_file == str(workbook)
    assert window._home_page._workspace_status.text() == (
        "Inspection failed · Invalid workbook"
    )
    critical.assert_called_once_with(
        window,
        "Workbook inspection failed",
        "The workbook could not be inspected.\n\nInvalid workbook",
    )
    settings_manager.add_recent_file.assert_not_called()


def test_execution_coordinator_runs_real_job_and_relays_controls(
    qtbot: object,
    qapp: QApplication,
    metadata: AppMetadata,
    theme_manager: MagicMock,
    settings_manager: MagicMock,
    workbook_inspector: MagicMock,
    tmp_path: Path,
) -> None:
    from PySide6.QtCore import QObject, Signal

    class Coordinator(QObject):
        progress = Signal(int, int, object, object)
        completed = Signal(object)
        stopped = Signal(object)
        failed = Signal(str)

        def __init__(self) -> None:
            super().__init__()
            self.start = MagicMock(return_value=True)
            self.pause = MagicMock()
            self.resume = MagicMock()
            self.stop = MagicMock()

    coordinator = Coordinator()
    workbook_inspector.inspect.side_effect = None
    workbook_inspector.inspect.return_value = WorkbookInfo(
        file_path="",
        file_name="routes.xlsx",
        file_type="XLSX",
        file_size_bytes=0,
        modified_at=datetime(2026, 8, 1, 8, 0),
        worksheets=(
            WorksheetInfo(
                name="Sheet1",
                row_count=3,
                column_count=3,
                headers=("Origin", "Destination", "Distance"),
                preview_rows=(
                    (
                        "10.762622,106.660172",
                        "10.823099,106.629664",
                        "",
                    ),
                    (
                        "10.823099,106.629664",
                        "10.776889,106.700806",
                        "",
                    ),
                ),
            ),
        ),
    )

    with patch(
        "app.presentation.main_window.qta.icon",
        return_value=QIcon(),
    ):
        result = MainWindow(
            application=qapp,
            metadata=metadata,
            theme_manager=theme_manager,
            settings_manager=settings_manager,
            workbook_inspector=workbook_inspector,
            execution_coordinator=coordinator,
        )
    qtbot.addWidget(result)  # type: ignore[attr-defined]

    workbook = tmp_path / "routes.xlsx"
    workbook.touch()
    result._select_workbook(str(workbook))
    assert result._home_page.selected_sheet_name == "Sheet1"
    assert result._home_page.workspace_ready
    assert result._action_start.isEnabled()

    result._action_start.trigger()
    coordinator.start.assert_called_once()
    job = coordinator.start.call_args.args[0]
    assert job.file_path == str(workbook)
    assert job.sheet_name == "Sheet1"
    assert result.execution_state is ExecutionState.RUNNING

    result._action_pause.trigger()
    coordinator.pause.assert_called_once_with()
    result._action_pause.trigger()
    coordinator.resume.assert_called_once_with()
    result._action_stop.trigger()
    coordinator.stop.assert_called_once_with()


def test_execution_coordinator_events_update_window(
    qtbot: object,
    qapp: QApplication,
    metadata: AppMetadata,
    theme_manager: MagicMock,
    settings_manager: MagicMock,
    workbook_inspector: MagicMock,
) -> None:
    from PySide6.QtCore import QObject, Signal

    class Coordinator(QObject):
        progress = Signal(int, int, object, object)
        completed = Signal(object)
        stopped = Signal(object)
        failed = Signal(str)

        def start(self, _job: object) -> bool:
            return True

        def pause(self) -> None:
            pass

        def resume(self) -> None:
            pass

        def stop(self) -> None:
            pass

    coordinator = Coordinator()
    with patch(
        "app.presentation.main_window.qta.icon",
        return_value=QIcon(),
    ):
        result = MainWindow(
            application=qapp,
            metadata=metadata,
            theme_manager=theme_manager,
            settings_manager=settings_manager,
            workbook_inspector=workbook_inspector,
            execution_coordinator=coordinator,
        )
    qtbot.addWidget(result)  # type: ignore[attr-defined]

    coordinator.progress.emit(2, 10, object(), object())
    assert result._status_label.text() == "Calculating route 2 of 10"

    result._set_execution_state(ExecutionState.RUNNING)
    coordinator.completed.emit([object(), object()])
    assert result.execution_state is ExecutionState.IDLE
    assert result._status_label.text() == "Calculation completed · 2 results"

    result._set_execution_state(ExecutionState.RUNNING)
    coordinator.stopped.emit([object()])
    assert result._status_label.text() == (
        "Calculation stopped · 1 results retained"
    )

    result._set_execution_state(ExecutionState.RUNNING)
    with patch.object(QMessageBox, "critical") as critical:
        coordinator.failed.emit("network error")
    critical.assert_called_once_with(
        result,
        "Calculation failed",
        "network error",
    )
    assert result._status_label.text() == "Calculation failed"

    result._on_calculation_completed(tuple())
    assert result._status_label.text() == "Calculation completed · 0 results"
    result._on_calculation_stopped(tuple())
    assert result._status_label.text() == (
        "Calculation stopped · 0 results retained"
    )


def test_execution_coordinator_rejects_start_and_missing_job_context(
    qtbot: object,
    qapp: QApplication,
    metadata: AppMetadata,
    theme_manager: MagicMock,
    settings_manager: MagicMock,
    workbook_inspector: MagicMock,
) -> None:
    from PySide6.QtCore import QObject, Signal

    class Coordinator(QObject):
        progress = Signal(int, int, object, object)
        completed = Signal(object)
        stopped = Signal(object)
        failed = Signal(str)

        def __init__(self) -> None:
            super().__init__()
            self.start = MagicMock(return_value=False)

        def pause(self) -> None:
            pass

        def resume(self) -> None:
            pass

        def stop(self) -> None:
            pass

    coordinator = Coordinator()
    with patch(
        "app.presentation.main_window.qta.icon",
        return_value=QIcon(),
    ):
        result = MainWindow(
            application=qapp,
            metadata=metadata,
            theme_manager=theme_manager,
            settings_manager=settings_manager,
            workbook_inspector=workbook_inspector,
            execution_coordinator=coordinator,
        )
    qtbot.addWidget(result)  # type: ignore[attr-defined]

    _make_workspace_ready(result)
    result._start_calculation()
    coordinator.start.assert_not_called()
    assert result.execution_state is ExecutionState.IDLE

    result._home_page.set_selected_file("routes.xlsx")
    _make_workspace_ready(result)
    result._start_calculation()
    coordinator.start.assert_called_once()
    assert result.execution_state is ExecutionState.IDLE
