from pathlib import Path

import qtawesome as qta
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QDragEnterEvent, QDragLeaveEvent, QDropEvent
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class HomePage(QWidget):
    """File-selection workspace used as the application's home page."""

    browse_requested = Signal()
    file_selected = Signal(str)

    SUPPORTED_EXTENSIONS = frozenset({".xlsx", ".xlsm", ".csv"})

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._selected_file: str | None = None
        self.setObjectName("pageWorkspace")
        self.setAcceptDrops(True)
        self._create_widgets()
        self._create_layout()
        self._connect_signals()
        self._apply_initial_state()

    @property
    def selected_file(self) -> str | None:
        return self._selected_file

    @classmethod
    def accepts_file(cls, file_path: str) -> bool:
        return Path(file_path).suffix.lower() in cls.SUPPORTED_EXTENSIONS

    def set_selected_file(self, file_path: str) -> None:
        normalized_path = str(Path(file_path))
        self._selected_file = normalized_path
        path = Path(normalized_path)
        self._selected_file_name.setText(path.name)
        self._selected_file_path.setText(normalized_path)
        self._selected_file_path.setToolTip(normalized_path)
        self._selected_file_frame.setVisible(True)
        self._empty_state_label.setVisible(False)
        self._workspace_status.setText("Workbook selected · Ready to inspect")

    def clear_selected_file(self) -> None:
        self._selected_file = None
        self._selected_file_frame.setVisible(False)
        self._empty_state_label.setVisible(True)
        self._workspace_status.setText("No workbook selected")

    def set_recent_files(self, file_paths: list[str]) -> None:
        self._recent_files.clear()
        if not file_paths:
            item = QListWidgetItem("No recent workbooks")
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self._recent_files.addItem(item)
            return

        for file_path in file_paths:
            path = Path(file_path)
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            self._recent_files.addItem(item)

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:  # noqa: N802
        if self._event_file_path(event) is not None:
            event.acceptProposedAction()
            self._drop_zone.setProperty("dragActive", True)
            self._drop_zone.style().unpolish(self._drop_zone)
            self._drop_zone.style().polish(self._drop_zone)
            return
        event.ignore()

    def dragLeaveEvent(self, event: QDragLeaveEvent) -> None:  # noqa: N802
        self._reset_drop_zone()
        super().dragLeaveEvent(event)

    def dropEvent(self, event: QDropEvent) -> None:  # noqa: N802
        file_path = self._event_file_path(event)
        self._reset_drop_zone()
        if file_path is None:
            event.ignore()
            return
        event.acceptProposedAction()
        self.file_selected.emit(file_path)

    def _create_widgets(self) -> None:
        self._title_label = QLabel("File Workspace", self)
        self._title_label.setObjectName("lblPageTitle")

        self._description_label = QLabel(
            "Select an Excel or CSV workbook to begin a distance-calculation job.",
            self,
        )
        self._description_label.setObjectName("lblPageDescription")
        self._description_label.setWordWrap(True)

        self._drop_zone = QFrame(self)
        self._drop_zone.setObjectName("frmDropZone")
        drop_layout = QVBoxLayout(self._drop_zone)
        drop_layout.setContentsMargins(28, 28, 28, 28)
        drop_layout.setSpacing(10)

        self._drop_icon = QLabel(self._drop_zone)
        self._drop_icon.setObjectName("lblDropIcon")
        self._drop_icon.setPixmap(qta.icon("fa5s.file-excel").pixmap(44, 44))
        self._drop_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._drop_title = QLabel("Drop a workbook here", self._drop_zone)
        self._drop_title.setObjectName("lblDropTitle")
        self._drop_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._drop_hint = QLabel(
            "Supported formats: .xlsx, .xlsm and .csv",
            self._drop_zone,
        )
        self._drop_hint.setObjectName("lblDropHint")
        self._drop_hint.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._browse_button = QPushButton("Browse files…", self._drop_zone)
        self._browse_button.setObjectName("btnBrowseWorkbook")
        self._browse_button.setIcon(qta.icon("fa5s.folder-open"))

        drop_layout.addWidget(self._drop_icon)
        drop_layout.addWidget(self._drop_title)
        drop_layout.addWidget(self._drop_hint)
        drop_layout.addWidget(
            self._browse_button,
            alignment=Qt.AlignmentFlag.AlignCenter,
        )

        self._selected_file_frame = QFrame(self)
        self._selected_file_frame.setObjectName("frmSelectedFile")
        selected_layout = QHBoxLayout(self._selected_file_frame)
        selected_layout.setContentsMargins(16, 12, 16, 12)
        selected_layout.setSpacing(12)

        self._selected_icon = QLabel(self._selected_file_frame)
        self._selected_icon.setPixmap(qta.icon("fa5s.file-alt").pixmap(28, 28))

        selected_text_layout = QVBoxLayout()
        selected_text_layout.setSpacing(2)
        self._selected_file_name = QLabel(self._selected_file_frame)
        self._selected_file_name.setObjectName("lblSelectedFileName")
        self._selected_file_path = QLabel(self._selected_file_frame)
        self._selected_file_path.setObjectName("lblSelectedFilePath")
        selected_text_layout.addWidget(self._selected_file_name)
        selected_text_layout.addWidget(self._selected_file_path)

        self._change_button = QPushButton("Change", self._selected_file_frame)
        self._change_button.setObjectName("btnChangeWorkbook")
        selected_layout.addWidget(self._selected_icon)
        selected_layout.addLayout(selected_text_layout, 1)
        selected_layout.addWidget(self._change_button)

        self._empty_state_label = QLabel(
            "Choose one workbook to activate the next workflow steps.",
            self,
        )
        self._empty_state_label.setObjectName("lblWorkspaceEmptyState")
        self._empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._recent_title = QLabel("Recent workbooks", self)
        self._recent_title.setObjectName("lblSectionTitle")
        self._recent_files = QListWidget(self)
        self._recent_files.setObjectName("lstRecentWorkbooks")
        self._recent_files.setMaximumHeight(170)

        self._workspace_status = QLabel(self)
        self._workspace_status.setObjectName("lblWorkspaceStatus")

    def _create_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(14)
        layout.addWidget(self._title_label)
        layout.addWidget(self._description_label)
        layout.addSpacing(4)
        layout.addWidget(self._drop_zone)
        layout.addWidget(self._selected_file_frame)
        layout.addWidget(self._empty_state_label)
        layout.addSpacing(6)
        layout.addWidget(self._recent_title)
        layout.addWidget(self._recent_files)
        layout.addWidget(self._workspace_status)
        layout.addStretch(1)

    def _connect_signals(self) -> None:
        self._browse_button.clicked.connect(self.browse_requested.emit)
        self._change_button.clicked.connect(self.browse_requested.emit)
        self._recent_files.itemActivated.connect(self._on_recent_file_activated)

    def _apply_initial_state(self) -> None:
        self.clear_selected_file()
        self.set_recent_files([])

    def _on_recent_file_activated(self, item: QListWidgetItem) -> None:
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(file_path, str):
            self.file_selected.emit(file_path)

    def _event_file_path(
        self,
        event: QDragEnterEvent | QDropEvent,
    ) -> str | None:
        urls = event.mimeData().urls()
        if len(urls) != 1 or not urls[0].isLocalFile():
            return None
        file_path = urls[0].toLocalFile()
        return file_path if self.accepts_file(file_path) else None

    def _reset_drop_zone(self) -> None:
        self._drop_zone.setProperty("dragActive", False)
        self._drop_zone.style().unpolish(self._drop_zone)
        self._drop_zone.style().polish(self._drop_zone)
