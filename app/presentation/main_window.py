from PySide6.QtCore import QSize
from PySide6.QtGui import QAction, QCloseEvent, QKeySequence
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
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
        self._action_exit = QAction("Exit", self)
        self._action_exit.setShortcut(QKeySequence.StandardKey.Quit)
        self._action_light_theme = QAction("Light Theme", self)
        self._action_light_theme.setCheckable(True)
        self._action_dark_theme = QAction("Dark Theme", self)
        self._action_dark_theme.setCheckable(True)
        self._action_start = QAction("Start", self)
        self._action_start.setShortcut(QKeySequence("F5"))
        self._action_pause = QAction("Pause", self)
        self._action_stop = QAction("Stop", self)
        self._action_settings = QAction("Settings", self)
        self._action_about = QAction("About", self)

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
        file_menu = self.menuBar().addMenu("File")
        file_menu.addAction(self._action_open)
        recent_menu = file_menu.addMenu("Recent Files")
        recent_menu.setEnabled(False)
        file_menu.addSeparator()
        file_menu.addAction(self._action_exit)
        view_menu = self.menuBar().addMenu("View")
        view_menu.addAction(self._action_light_theme)
        view_menu.addAction(self._action_dark_theme)
        self.menuBar().addMenu("Tools")
        help_menu = self.menuBar().addMenu("Help")
        help_menu.addAction(self._action_about)

    def _create_toolbar(self) -> None:
        toolbar = QToolBar("Main Toolbar", self)
        toolbar.setObjectName("tbMain")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.addAction(self._action_open)
        toolbar.addSeparator()
        toolbar.addAction(self._action_start)
        toolbar.addAction(self._action_pause)
        toolbar.addAction(self._action_stop)
        toolbar.addSeparator()
        toolbar.addAction(self._action_settings)
        self.addToolBar(toolbar)

    def _create_status_bar(self) -> None:
        self._status_label = QLabel("Ready")
        self._provider_label = QLabel("Provider: -")
        self._theme_label = QLabel()
        self._version_label = QLabel(
            f"{self._metadata.name} v{self._metadata.version}"
        )
        self.statusBar().addWidget(self._status_label, 1)
        self.statusBar().addPermanentWidget(self._provider_label)
        self.statusBar().addPermanentWidget(self._theme_label)
        self.statusBar().addPermanentWidget(self._version_label)

    def _connect_signals(self) -> None:
        self._navigation.page_changed.connect(self._content_stack.setCurrentIndex)
        self._action_exit.triggered.connect(self.close)
        self._action_light_theme.triggered.connect(self._on_light_theme_selected)
        self._action_dark_theme.triggered.connect(self._on_dark_theme_selected)
        self._action_settings.triggered.connect(self._show_settings_page)
        self._action_about.triggered.connect(self._show_about_dialog)
        self._action_open.triggered.connect(self._show_sprint_placeholder)
        self._action_start.triggered.connect(self._show_sprint_placeholder)
        self._action_pause.triggered.connect(self._show_sprint_placeholder)
        self._action_stop.triggered.connect(self._show_sprint_placeholder)

    def _apply_initial_state(self) -> None:
        self.setWindowTitle(self._metadata.name)
        self.resize(1280, 800)
        self.setMinimumSize(1100, 700)
        self._restore_window_state()
        self._update_theme_state(self._theme_manager.current_theme)

    def _on_light_theme_selected(self) -> None:
        self._apply_theme("light")

    def _on_dark_theme_selected(self) -> None:
        self._apply_theme("dark")

    def _show_settings_page(self) -> None:
        self._navigation.setCurrentRow(2)

    def _show_about_dialog(self) -> None:
        AboutDialog(self._metadata, self).exec()

    def _apply_theme(self, theme_name: str) -> None:
        self._theme_manager.apply_theme(self._application, theme_name)
        self._settings_manager.set_theme_name(theme_name)
        self._update_theme_state(theme_name)

    def _update_theme_state(self, theme_name: str) -> None:
        self._theme_label.setText(f"Theme: {theme_name.capitalize()}")
        self._action_light_theme.setChecked(theme_name == "light")
        self._action_dark_theme.setChecked(theme_name == "dark")

    def _restore_window_state(self) -> None:
        geometry = self._settings_manager.window_geometry()
        state = self._settings_manager.window_state()
        if geometry is not None:
            self.restoreGeometry(geometry)
        if state is not None:
            self.restoreState(state)

    def _show_sprint_placeholder(self) -> None:
        QMessageBox.information(
            self,
            "Sprint 1A.1",
            "This command will be connected in a later sprint.",
        )

    def closeEvent(self, event: QCloseEvent) -> None:  # noqa: N802
        self._settings_manager.set_window_geometry(bytes(self.saveGeometry()))
        self._settings_manager.set_window_state(bytes(self.saveState()))
        event.accept()
