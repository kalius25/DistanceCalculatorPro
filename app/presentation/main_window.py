from pathlib import Path

import qtawesome as qta
from PySide6.QtCore import Signal
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStackedWidget,
    QToolBar,
    QWidget,
)

from app.batch.progress import ProgressSnapshot
from app.batch.summary import BatchSummary
from app.diagnostics import DiagnosticsManager, DiagnosticsSettings
from app.logging import LoggingManager
from app.workbooks import (
    CsvWorkbookReader,
    OpenPyXLWorkbookReader,
    WorkbookInspectorService,
)

from .app_metadata import AppMetadata
from .dialogs.about_dialog import AboutDialog
from .execution import CalculationExecutionCoordinator, CalculationJob
from .models.execution_state import ExecutionState
from .pages.about_page import AboutPage
from .pages.history_page import HistoryPage
from .pages.home_page import HomePage
from .pages.settings_page import SettingsPage
from .settings_manager import SettingsManager
from .theme_manager import ThemeManager
from .widgets.navigation_panel import NavigationPanel


class MainWindow(QMainWindow):
    """Top-level presentation shell for DistanceCalculatorPro."""

    calculation_requested = Signal(object)
    calculation_pause_requested = Signal()
    calculation_resume_requested = Signal()
    calculation_stop_requested = Signal()
    calculation_progress = Signal(int, int, object, object)
    calculation_metrics = Signal(object)
    calculation_completed = Signal(object)
    calculation_stopped = Signal(object)
    calculation_failed = Signal(str)
    calculation_summary = Signal(object)

    HOME_PAGE_INDEX = 0
    HISTORY_PAGE_INDEX = 1
    SETTINGS_PAGE_INDEX = 2
    ABOUT_PAGE_INDEX = 3

    PAGE_NAMES = ("Home", "History", "Settings", "About")

    LIGHT_ICON_COLOR = "#111827"
    DARK_ICON_COLOR = "#F8FAFC"
    DISABLED_ICON_COLOR = "#9CA3AF"

    def __init__(
        self,
        application: QApplication,
        metadata: AppMetadata,
        theme_manager: ThemeManager,
        settings_manager: SettingsManager,
        workbook_inspector: WorkbookInspectorService | None = None,
        execution_coordinator: CalculationExecutionCoordinator | None = None,
        diagnostics_manager: DiagnosticsManager | None = None,
    ) -> None:
        super().__init__()
        self._application = application
        self._metadata = metadata
        self._theme_manager = theme_manager
        self._settings_manager = settings_manager
        self._execution_state = ExecutionState.IDLE
        self._execution_coordinator = execution_coordinator
        self._last_summary: BatchSummary | None = None
        self._diagnostics_manager = diagnostics_manager or DiagnosticsManager()
        self._workbook_inspector = workbook_inspector or WorkbookInspectorService(
            (OpenPyXLWorkbookReader(), CsvWorkbookReader())
        )

        self._create_actions()
        self._create_widgets()
        self._create_layout()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._connect_signals()
        self._apply_initial_state()

    @property
    def execution_state(self) -> ExecutionState:
        return self._execution_state

    def _create_actions(self) -> None:
        self._action_open = QAction("Open Excel", self)
        self._action_open.setShortcut(QKeySequence.StandardKey.Open)
        self._action_open.setToolTip("Open an Excel workbook (Ctrl+O)")

        self._action_exit = QAction("Exit", self)
        self._action_exit.setShortcut(QKeySequence.StandardKey.Quit)

        self._action_light_theme = QAction("Light Theme", self)
        self._action_light_theme.setCheckable(True)
        self._action_dark_theme = QAction("Dark Theme", self)
        self._action_dark_theme.setCheckable(True)

        self._theme_action_group = QActionGroup(self)
        self._theme_action_group.setExclusive(True)
        self._theme_action_group.addAction(self._action_light_theme)
        self._theme_action_group.addAction(self._action_dark_theme)

        self._action_start = QAction("Start", self)
        self._action_start.setShortcut(QKeySequence("F5"))
        self._action_start.setToolTip("Start calculation (F5)")

        self._action_pause = QAction("Pause", self)
        self._action_pause.setShortcut(QKeySequence("F6"))
        self._action_pause.setToolTip("Pause calculation (F6)")

        self._action_stop = QAction("Stop", self)
        self._action_stop.setShortcut(QKeySequence("Shift+F5"))
        self._action_stop.setToolTip("Stop calculation (Shift+F5)")

        self._action_retry_failed = QAction("Retry Failed", self)
        self._action_retry_failed.setToolTip(
            "Run only rows that failed in the previous batch"
        )

        self._action_settings = QAction("Settings", self)
        self._action_settings.setShortcut(QKeySequence("Ctrl+,"))
        self._action_settings.setToolTip("Open settings (Ctrl+,)")

        self._action_debug_mode = QAction("Debug Mode", self)
        self._action_debug_mode.setCheckable(True)
        self._action_trace_browser = QAction("Trace Browser", self)
        self._action_trace_browser.setCheckable(True)
        self._action_parser_diagnostics = QAction("Parser Diagnostics", self)
        self._action_parser_diagnostics.setCheckable(True)
        self._action_save_html = QAction("Save HTML", self)
        self._action_save_html.setCheckable(True)
        self._action_save_screenshot = QAction("Save Screenshot", self)
        self._action_save_screenshot.setCheckable(True)
        self._action_save_json = QAction("Save Parser JSON", self)
        self._action_save_json.setCheckable(True)

        self._action_about = QAction("About", self)
        self._action_home = self._create_navigation_action(
            "Home",
            "Ctrl+1",
            self.HOME_PAGE_INDEX,
        )
        self._action_history = self._create_navigation_action(
            "History",
            "Ctrl+2",
            self.HISTORY_PAGE_INDEX,
        )
        self._action_settings_page = self._create_navigation_action(
            "Settings Page",
            "Ctrl+3",
            self.SETTINGS_PAGE_INDEX,
        )
        self._action_about_page = self._create_navigation_action(
            "About Page",
            "Ctrl+4",
            self.ABOUT_PAGE_INDEX,
        )

    def _create_navigation_action(
        self,
        text: str,
        shortcut: str,
        page_index: int,
    ) -> QAction:
        action = QAction(text, self)
        action.setShortcut(QKeySequence(shortcut))
        action.setData(page_index)
        self.addAction(action)
        return action

    def _create_widgets(self) -> None:
        self._navigation = NavigationPanel(self)
        self._content_stack = QStackedWidget(self)
        self._content_stack.setObjectName("stkContent")
        self._home_page = HomePage(self)
        self._content_stack.addWidget(self._home_page)
        self._content_stack.addWidget(HistoryPage(self))
        self._content_stack.addWidget(SettingsPage(self))
        self._content_stack.addWidget(AboutPage(self))

    def _create_layout(self) -> None:
        central_widget = QWidget(self)
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._navigation)
        layout.addWidget(self._content_stack, 1)
        self.setCentralWidget(central_widget)

    def _create_menu_bar(self) -> None:
        menu_bar = self.menuBar()

        self._file_menu: QMenu = menu_bar.addMenu("&File")
        self._file_menu.addAction(self._action_open)
        self._recent_files_menu: QMenu = self._file_menu.addMenu("Recent Files")
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._action_exit)

        self._view_menu: QMenu = menu_bar.addMenu("&View")
        self._view_menu.addAction(self._action_light_theme)
        self._view_menu.addAction(self._action_dark_theme)

        self._debug_menu: QMenu = menu_bar.addMenu("&Debug")
        self._debug_menu.addAction(self._action_debug_mode)
        self._debug_menu.addSeparator()
        self._debug_menu.addAction(self._action_trace_browser)
        self._debug_menu.addAction(self._action_parser_diagnostics)
        self._debug_menu.addSeparator()
        self._debug_menu.addAction(self._action_save_html)
        self._debug_menu.addAction(self._action_save_screenshot)
        self._debug_menu.addAction(self._action_save_json)

        self._help_menu: QMenu = menu_bar.addMenu("&Help")
        self._help_menu.addAction(self._action_about)

    def _create_toolbar(self) -> None:
        self._toolbar = QToolBar("Main Toolbar", self)
        self._toolbar.setObjectName("main_toolbar")
        self._toolbar.setMovable(False)
        self._toolbar.addAction(self._action_open)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._action_start)
        self._toolbar.addAction(self._action_pause)
        self._toolbar.addAction(self._action_stop)
        self._toolbar.addAction(self._action_retry_failed)
        self._toolbar.addSeparator()
        self._toolbar.addAction(self._action_settings)
        self.addToolBar(self._toolbar)

        self._view_menu.addSeparator()
        self._view_menu.addAction(self._toolbar.toggleViewAction())

    def _create_status_bar(self) -> None:
        self._status_label = QLabel("Ready", self)
        self._status_label.setObjectName("lblStatus")
        self._provider_label = QLabel("Provider: -", self)
        self._provider_label.setObjectName("lblProvider")
        self._theme_label = QLabel(self)
        self._theme_label.setObjectName("lblTheme")
        self._version_label = QLabel(
            f"{self._metadata.name} v{self._metadata.version}",
            self,
        )
        self._version_label.setObjectName("lblVersion")

        status_bar = self.statusBar()
        status_bar.addWidget(self._status_label, 1)
        status_bar.addPermanentWidget(self._provider_label)
        status_bar.addPermanentWidget(self._theme_label)
        status_bar.addPermanentWidget(self._version_label)

    def _connect_signals(self) -> None:
        self._navigation.page_changed.connect(self._content_stack.setCurrentIndex)
        self._content_stack.currentChanged.connect(self._on_current_page_changed)
        self._action_exit.triggered.connect(self.close)
        self._action_light_theme.triggered.connect(self._on_light_theme_selected)
        self._action_dark_theme.triggered.connect(self._on_dark_theme_selected)
        self._action_settings.triggered.connect(self._show_settings_page)
        self._action_about.triggered.connect(self._show_about_dialog)
        self._action_open.triggered.connect(self._browse_for_workbook)
        self._home_page.browse_requested.connect(self._browse_for_workbook)
        self._home_page.file_selected.connect(self._select_workbook)
        self._home_page.clear_recent_requested.connect(self._clear_recent_files)
        self._action_start.triggered.connect(self._start_calculation)
        self._action_pause.triggered.connect(self._toggle_pause)
        self._action_stop.triggered.connect(self._stop_calculation)
        self._action_retry_failed.triggered.connect(self._retry_failed)
        self._home_page.retry_failed_requested.connect(self._retry_failed)
        self._home_page.workspace_ready_changed.connect(
            self._on_workspace_ready_changed
        )
        if self._execution_coordinator is not None:
            self._execution_coordinator.progress.connect(self._on_calculation_progress)
            self._execution_coordinator.metrics.connect(self._on_calculation_metrics)
            self._execution_coordinator.completed.connect(
                self._on_calculation_completed
            )
            self._execution_coordinator.stopped.connect(self._on_calculation_stopped)
            self._execution_coordinator.failed.connect(self._on_calculation_failed)
            summary_signal = getattr(
                self._execution_coordinator,
                "summary",
                None,
            )
            if summary_signal is not None:
                summary_signal.connect(self._on_calculation_summary)
        self._action_debug_mode.toggled.connect(self._on_diagnostics_changed)
        self._action_trace_browser.toggled.connect(self._on_diagnostics_changed)
        self._action_parser_diagnostics.toggled.connect(self._on_diagnostics_changed)
        self._action_save_html.toggled.connect(self._on_diagnostics_changed)
        self._action_save_screenshot.toggled.connect(self._on_diagnostics_changed)
        self._action_save_json.toggled.connect(self._on_diagnostics_changed)
        self._action_home.triggered.connect(self._show_action_page)
        self._action_history.triggered.connect(self._show_action_page)
        self._action_settings_page.triggered.connect(self._show_action_page)
        self._action_about_page.triggered.connect(self._show_action_page)
        self._toolbar.visibilityChanged.connect(
            self._settings_manager.set_toolbar_visible
        )

    def _apply_initial_state(self) -> None:
        self.setWindowTitle(self._metadata.name)
        self.resize(1280, 800)
        self.setMinimumSize(1100, 700)
        self._restore_window_state()
        self._toolbar.setVisible(self._settings_manager.toolbar_visible())
        self._update_recent_files_menu()
        self._home_page.set_recent_files(self._settings_manager.recent_files())
        self._update_theme_state(self._theme_manager.current_theme)
        self._on_current_page_changed(self._content_stack.currentIndex())
        self._load_diagnostics_state()
        self._update_execution_actions()

    def _load_diagnostics_state(self) -> None:
        actions = (
            (self._action_debug_mode, "debug_enabled"),
            (self._action_trace_browser, "trace_browser"),
            (self._action_parser_diagnostics, "parser_diagnostics"),
            (self._action_save_html, "save_html"),
            (self._action_save_screenshot, "save_screenshot"),
            (self._action_save_json, "save_json"),
        )
        for action, method_name in actions:
            method = getattr(self._settings_manager, method_name, None)
            value = method() if callable(method) else False
            action.blockSignals(True)
            action.setChecked(value if isinstance(value, bool) else False)
            action.blockSignals(False)
        self._apply_diagnostics_state(persist=False)

    def _on_diagnostics_changed(self, _checked: bool) -> None:
        self._apply_diagnostics_state(persist=True)

    def _apply_diagnostics_state(self, *, persist: bool) -> None:
        enabled = self._action_debug_mode.isChecked()
        dependent_actions = (
            self._action_trace_browser,
            self._action_parser_diagnostics,
            self._action_save_html,
            self._action_save_screenshot,
            self._action_save_json,
        )
        for action in dependent_actions:
            action.setEnabled(enabled)

        settings = DiagnosticsSettings(
            enabled=enabled,
            trace_browser=self._action_trace_browser.isChecked(),
            parser_diagnostics=(self._action_parser_diagnostics.isChecked()),
            save_html=self._action_save_html.isChecked(),
            save_screenshot=self._action_save_screenshot.isChecked(),
            save_json=self._action_save_json.isChecked(),
        )
        self._diagnostics_manager.update(settings)
        LoggingManager.set_debug_enabled(enabled)
        if persist:
            self._settings_manager.set_debug_enabled(enabled)
            self._settings_manager.set_trace_browser(settings.trace_browser)
            self._settings_manager.set_parser_diagnostics(settings.parser_diagnostics)
            self._settings_manager.set_save_html(settings.save_html)
            self._settings_manager.set_save_screenshot(settings.save_screenshot)
            self._settings_manager.set_save_json(settings.save_json)

    def _on_light_theme_selected(self) -> None:
        self._apply_theme("light")

    def _on_dark_theme_selected(self) -> None:
        self._apply_theme("dark")

    def _show_settings_page(self) -> None:
        self._navigation.setCurrentRow(self.SETTINGS_PAGE_INDEX)

    def _show_about_dialog(self) -> None:
        AboutDialog(self._metadata, self).exec()

    def _show_action_page(self) -> None:
        action = self.sender()
        if isinstance(action, QAction):
            self._navigation.setCurrentRow(int(action.data()))

    def _on_current_page_changed(self, page_index: int) -> None:
        if 0 <= page_index < len(self.PAGE_NAMES):
            page_name = self.PAGE_NAMES[page_index]
            self._status_label.setText(f"Ready · {page_name}")

    def _apply_theme(self, theme_name: str) -> None:
        self._theme_manager.apply_theme(self._application, theme_name)
        self._settings_manager.set_theme_name(theme_name)
        self._update_theme_state(theme_name)

    def _update_theme_state(self, theme_name: str) -> None:
        self._theme_label.setText(f"Theme: {theme_name.capitalize()}")
        self._action_light_theme.setChecked(theme_name == "light")
        self._action_dark_theme.setChecked(theme_name == "dark")
        self._update_action_icons(theme_name)

    def _update_action_icons(self, theme_name: str) -> None:
        icon_color = (
            self.LIGHT_ICON_COLOR if theme_name == "light" else self.DARK_ICON_COLOR
        )
        icon_options = {
            "color": icon_color,
            "color_disabled": self.DISABLED_ICON_COLOR,
        }

        self._action_open.setIcon(qta.icon("fa5s.folder-open", **icon_options))
        self._action_start.setIcon(qta.icon("fa5s.play", **icon_options))
        self._action_pause.setIcon(qta.icon("fa5s.pause", **icon_options))
        self._action_stop.setIcon(qta.icon("fa5s.stop", **icon_options))
        self._action_retry_failed.setIcon(qta.icon("fa5s.redo", **icon_options))
        self._action_settings.setIcon(qta.icon("fa5s.cog", **icon_options))

    def _restore_window_state(self) -> None:
        geometry = self._settings_manager.window_geometry()
        state = self._settings_manager.window_state()
        if geometry is not None:
            self.restoreGeometry(geometry)
        if state is not None:
            self.restoreState(state)

    def _update_recent_files_menu(self) -> None:
        self._recent_files_menu.clear()
        recent_files = self._settings_manager.recent_files()
        if not recent_files:
            empty_action = self._recent_files_menu.addAction("No recent files")
            empty_action.setEnabled(False)
            return

        for file_path in recent_files:
            action = self._recent_files_menu.addAction(Path(file_path).name)
            action.setToolTip(file_path)
            action.setData(file_path)
            action.triggered.connect(self._show_recent_file_placeholder)

        self._recent_files_menu.addSeparator()
        clear_action = self._recent_files_menu.addAction("Clear Recent Files")
        clear_action.triggered.connect(self._clear_recent_files)

    def _browse_for_workbook(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open workbook",
            "",
            "Supported workbooks (*.xlsx *.xlsm *.csv);;"
            "Excel workbooks (*.xlsx *.xlsm);;CSV files (*.csv)",
        )
        if file_path:
            self._select_workbook(file_path)

    def _select_workbook(self, file_path: str) -> None:
        path = Path(file_path)
        if not path.is_file():
            QMessageBox.warning(
                self,
                "Workbook unavailable",
                f"The selected workbook does not exist.\n\n{file_path}",
            )
            return
        if not HomePage.accepts_file(file_path):
            QMessageBox.warning(
                self,
                "Unsupported workbook",
                "Select an .xlsx, .xlsm or .csv file.",
            )
            return

        normalized_path = str(path)
        try:
            workbook_info = self._workbook_inspector.inspect(normalized_path)
        except (OSError, ValueError) as error:
            self._home_page.set_selected_file(normalized_path)
            self._home_page.set_inspection_error(str(error))
            QMessageBox.critical(
                self,
                "Workbook inspection failed",
                f"The workbook could not be inspected.\n\n{error}",
            )
            return

        self._home_page.set_selected_file(normalized_path)
        self._home_page.set_inspection(workbook_info)
        self._settings_manager.add_recent_file(normalized_path)
        self._update_recent_files_menu()
        self._home_page.set_recent_files(self._settings_manager.recent_files())
        self._navigation.setCurrentRow(self.HOME_PAGE_INDEX)
        self._status_label.setText(f"Ready · {path.name}")

    def _show_recent_file_placeholder(self) -> None:
        action = self.sender()
        if isinstance(action, QAction):
            self._select_workbook(str(action.data()))

    def _clear_recent_files(self) -> None:
        self._settings_manager.clear_recent_files()
        self._update_recent_files_menu()
        self._home_page.set_recent_files([])

    def _on_workspace_ready_changed(self, _ready: bool) -> None:
        self._update_execution_actions()

    def _start_calculation(self) -> None:
        configuration = self._home_page.workspace_configuration
        file_path = self._home_page.selected_file
        sheet_name = self._home_page.selected_sheet_name
        if self._execution_state is not ExecutionState.IDLE or configuration is None:
            return

        if self._execution_coordinator is not None:
            if file_path is None or sheet_name is None:
                return
            job = CalculationJob(file_path, sheet_name, configuration)
            if not self._execution_coordinator.start(job):
                return

        self._home_page.clear_batch_summary()
        self._last_summary = None
        self._set_execution_state(ExecutionState.RUNNING)
        self.calculation_requested.emit(configuration)

    def _retry_failed(self) -> None:
        if (
            self._execution_state is not ExecutionState.IDLE
            or self._execution_coordinator is None
            or not self._execution_coordinator.retry_failed()
        ):
            return
        self._set_execution_state(ExecutionState.RUNNING)
        self._status_label.setText("Retrying failed routes")

    def _toggle_pause(self) -> None:
        if self._execution_state is ExecutionState.RUNNING:
            if self._execution_coordinator is not None:
                self._execution_coordinator.pause()
            self._set_execution_state(ExecutionState.PAUSED)
            self.calculation_pause_requested.emit()
        elif self._execution_state is ExecutionState.PAUSED:
            if self._execution_coordinator is not None:
                self._execution_coordinator.resume()
            self._set_execution_state(ExecutionState.RUNNING)
            self.calculation_resume_requested.emit()

    def _stop_calculation(self) -> None:
        if self._execution_state is ExecutionState.IDLE:
            return
        if self._execution_coordinator is not None:
            self._execution_coordinator.stop()
        self._set_execution_state(ExecutionState.IDLE)
        self.calculation_stop_requested.emit()

    def _on_calculation_progress(
        self,
        current: int,
        total: int,
        _request: object,
        _result: object,
    ) -> None:
        self._status_label.setText(f"Calculating route {current:,} of {total:,}")
        self.calculation_progress.emit(
            current,
            total,
            _request,
            _result,
        )

    def _on_calculation_metrics(self, metrics: object) -> None:
        if not isinstance(metrics, ProgressSnapshot):
            return
        elapsed = self._format_duration(metrics.elapsed_seconds)
        eta = self._format_duration(metrics.eta_seconds)
        self._status_label.setText(
            f"{metrics.completed:,}/{metrics.total:,} · "
            f"{metrics.percent_complete:.0f}% · "
            f"{metrics.items_per_minute:.1f} jobs/min · "
            f"Elapsed {elapsed} · ETA {eta}"
        )
        self.calculation_metrics.emit(metrics)

    @staticmethod
    def _format_duration(seconds: float) -> str:
        total_seconds = max(int(round(seconds)), 0)
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds_value = divmod(remainder, 60)
        if hours:
            return f"{hours:02d}:{minutes:02d}:{seconds_value:02d}"
        return f"{minutes:02d}:{seconds_value:02d}"

    def _on_calculation_summary(self, summary: object) -> None:
        if not isinstance(summary, BatchSummary):
            return
        self._last_summary = summary
        self._home_page.set_batch_summary(summary)
        self._status_label.setText(
            f"Completed {summary.successful:,}/{summary.total:,} · "
            f"Failed {summary.failed:,} · Retried {summary.retry_count:,}"
        )
        self.calculation_summary.emit(summary)
        self._update_execution_actions()

    def _on_calculation_completed(self, results: object) -> None:
        result_count = len(results) if isinstance(results, list) else 0
        self._set_execution_state(ExecutionState.IDLE)
        self._status_label.setText(f"Calculation completed · {result_count:,} results")
        self.calculation_completed.emit(results)

    def _on_calculation_stopped(self, results: object) -> None:
        result_count = len(results) if isinstance(results, list) else 0
        self._set_execution_state(ExecutionState.IDLE)
        self._status_label.setText(
            f"Calculation stopped · {result_count:,} results retained"
        )
        self.calculation_stopped.emit(results)

    def _on_calculation_failed(self, message: str) -> None:
        self._set_execution_state(ExecutionState.IDLE)
        self._status_label.setText("Calculation failed")
        self.calculation_failed.emit(message)
        QMessageBox.critical(
            self,
            "Calculation failed",
            message,
        )

    def _set_execution_state(self, state: ExecutionState) -> None:
        if state is self._execution_state:
            return
        self._execution_state = state
        self._home_page.set_workspace_locked(state is not ExecutionState.IDLE)
        self._update_execution_actions()

    def _update_execution_actions(self) -> None:
        idle = self._execution_state is ExecutionState.IDLE
        running = self._execution_state is ExecutionState.RUNNING
        paused = self._execution_state is ExecutionState.PAUSED

        self._action_start.setEnabled(idle and self._home_page.workspace_ready)
        self._action_pause.setEnabled(running or paused)
        self._action_stop.setEnabled(running or paused)
        self._action_retry_failed.setEnabled(
            idle and self._last_summary is not None and self._last_summary.failed > 0
        )
        self._action_open.setEnabled(idle)

        self._action_pause.setText("Resume" if paused else "Pause")
        self._action_pause.setToolTip(
            "Resume calculation (F6)" if paused else "Pause calculation (F6)"
        )

        if running:
            self._status_label.setText("Calculation running")
        elif paused:
            self._status_label.setText("Calculation paused")
        elif self._home_page.workspace_ready:
            self._status_label.setText("Ready to calculate")

    def shutdown(self, timeout_ms: int = 5_000) -> bool:
        """Stop background execution and release runtime resources."""
        if self._execution_coordinator is None:
            return True
        return self._execution_coordinator.shutdown(timeout_ms)

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        if (
            self._execution_coordinator is not None
            and self._execution_coordinator.is_running
        ):
            answer = QMessageBox.question(
                self,
                "Calculation in progress",
                (
                    "A calculation is still running. Stop it and close "
                    "DistanceCalculatorPro?"
                ),
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )
            if answer != QMessageBox.StandardButton.Yes:
                event.ignore()
                return

        if not self.shutdown():
            QMessageBox.warning(
                self,
                "Shutdown delayed",
                "The calculation worker did not stop in time. Please try again.",
            )
            event.ignore()
            return

        self._settings_manager.set_window_geometry(self.saveGeometry())
        self._settings_manager.set_window_state(self.saveState())
        self._settings_manager.set_toolbar_visible(self._toolbar.isVisible())
        event.accept()
