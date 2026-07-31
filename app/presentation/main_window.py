from pathlib import Path

import qtawesome as qta
from PySide6.QtGui import QAction, QActionGroup, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QStackedWidget,
    QToolBar,
    QWidget,
)

from .app_metadata import AppMetadata
from .dialogs.about_dialog import AboutDialog
from .pages.about_page import AboutPage
from .pages.history_page import HistoryPage
from .pages.home_page import HomePage
from .pages.settings_page import SettingsPage
from .settings_manager import SettingsManager
from .theme_manager import ThemeManager
from .widgets.navigation_panel import NavigationPanel


class MainWindow(QMainWindow):
    """Top-level presentation shell for DistanceCalculatorPro."""

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
    ) -> None:
        super().__init__()
        self._application = application
        self._metadata = metadata
        self._theme_manager = theme_manager
        self._settings_manager = settings_manager

        self._create_actions()
        self._create_widgets()
        self._create_layout()
        self._create_menu_bar()
        self._create_toolbar()
        self._create_status_bar()
        self._connect_signals()
        self._apply_initial_state()

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

        self._action_settings = QAction("Settings", self)
        self._action_settings.setShortcut(QKeySequence("Ctrl+,"))
        self._action_settings.setToolTip("Open settings (Ctrl+,)")

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
        self._content_stack.addWidget(HomePage(self))
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
        self._recent_files_menu: QMenu = self._file_menu.addMenu(
            "Recent Files"
        )
        self._file_menu.addSeparator()
        self._file_menu.addAction(self._action_exit)

        self._view_menu: QMenu = menu_bar.addMenu("&View")
        self._view_menu.addAction(self._action_light_theme)
        self._view_menu.addAction(self._action_dark_theme)

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
        self._content_stack.currentChanged.connect(
            self._on_current_page_changed
        )
        self._action_exit.triggered.connect(self.close)
        self._action_light_theme.triggered.connect(self._on_light_theme_selected)
        self._action_dark_theme.triggered.connect(self._on_dark_theme_selected)
        self._action_settings.triggered.connect(self._show_settings_page)
        self._action_about.triggered.connect(self._show_about_dialog)
        self._action_open.triggered.connect(self._show_sprint_placeholder)
        self._action_start.triggered.connect(self._show_sprint_placeholder)
        self._action_pause.triggered.connect(self._show_sprint_placeholder)
        self._action_stop.triggered.connect(self._show_sprint_placeholder)
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
        self._update_theme_state(self._theme_manager.current_theme)
        self._on_current_page_changed(self._content_stack.currentIndex())

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
            self.LIGHT_ICON_COLOR
            if theme_name == "light"
            else self.DARK_ICON_COLOR
        )
        icon_options = {
            "color": icon_color,
            "color_disabled": self.DISABLED_ICON_COLOR,
        }

        self._action_open.setIcon(
            qta.icon("fa5s.folder-open", **icon_options)
        )
        self._action_start.setIcon(qta.icon("fa5s.play", **icon_options))
        self._action_pause.setIcon(qta.icon("fa5s.pause", **icon_options))
        self._action_stop.setIcon(qta.icon("fa5s.stop", **icon_options))
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

    def _show_recent_file_placeholder(self) -> None:
        action = self.sender()
        if not isinstance(action, QAction):
            return
        file_path = str(action.data())
        QMessageBox.information(
            self,
            "Recent File",
            "Workbook opening will be connected in Sprint 1B."
            f"\n\n{file_path}",
        )

    def _clear_recent_files(self) -> None:
        self._settings_manager.clear_recent_files()
        self._update_recent_files_menu()

    def _show_sprint_placeholder(self) -> None:
        QMessageBox.information(
            self,
            "Sprint 1A.2",
            "This command will be connected in a later sprint.",
        )

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._settings_manager.set_window_geometry(self.saveGeometry())
        self._settings_manager.set_window_state(self.saveState())
        self._settings_manager.set_toolbar_visible(self._toolbar.isVisible())
        event.accept()
