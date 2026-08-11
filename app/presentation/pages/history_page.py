from pathlib import Path

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class HistoryPage(QWidget):
    """Recent-workbook history with explicit open/remove/clear actions."""

    open_requested = Signal(str)
    remove_requested = Signal(str)
    clear_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._create_layout()
        self.set_recent_files([])

    def _create_layout(self) -> None:
        title = QLabel("History")
        title.setObjectName("lblPageTitle")

        description = QLabel(
            "Recently opened workbooks. Open an item again or remove stale entries."
        )
        description.setObjectName("lblPageDescription")
        description.setWordWrap(True)

        self._recent_files = QListWidget()
        self._recent_files.setObjectName("lstHistoryRecentFiles")
        self._recent_files.currentItemChanged.connect(self._update_actions)
        self._recent_files.itemDoubleClicked.connect(self._open_item)

        self._open_button = QPushButton("Open")
        self._open_button.setObjectName("btnHistoryOpen")
        self._open_button.clicked.connect(self._open_selected)

        self._remove_button = QPushButton("Remove")
        self._remove_button.setObjectName("btnHistoryRemove")
        self._remove_button.clicked.connect(self._remove_selected)

        self._clear_button = QPushButton("Clear history")
        self._clear_button.setObjectName("btnHistoryClear")
        self._clear_button.clicked.connect(self.clear_requested.emit)

        buttons = QHBoxLayout()
        buttons.addWidget(self._open_button)
        buttons.addWidget(self._remove_button)
        buttons.addStretch()
        buttons.addWidget(self._clear_button)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addWidget(self._recent_files, 1)
        layout.addLayout(buttons)

    def set_recent_files(self, recent_files: list[str]) -> None:
        self._recent_files.clear()
        for file_path in recent_files:
            path = Path(file_path)
            item = QListWidgetItem(path.name)
            item.setData(Qt.ItemDataRole.UserRole, file_path)
            item.setToolTip(file_path)
            self._recent_files.addItem(item)

        has_items = bool(recent_files)
        if not has_items:
            empty_item = QListWidgetItem("No recent workbooks")
            empty_item.setFlags(empty_item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
            self._recent_files.addItem(empty_item)

        self._clear_button.setEnabled(has_items)
        self._update_actions()

    @property
    def recent_files(self) -> list[str]:
        files: list[str] = []
        for row in range(self._recent_files.count()):
            item = self._recent_files.item(row)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            if isinstance(file_path, str):
                files.append(file_path)
        return files

    def _selected_path(self) -> str | None:
        item = self._recent_files.currentItem()
        if item is None:
            return None
        file_path = item.data(Qt.ItemDataRole.UserRole)
        return file_path if isinstance(file_path, str) else None

    def _update_actions(self, *_args: object) -> None:
        has_selection = self._selected_path() is not None
        self._open_button.setEnabled(has_selection)
        self._remove_button.setEnabled(has_selection)

    def _open_selected(self) -> None:
        file_path = self._selected_path()
        if file_path is not None:
            self.open_requested.emit(file_path)
        else:
            self._update_actions()

    def _remove_selected(self) -> None:
        file_path = self._selected_path()
        if file_path is not None:
            self.remove_requested.emit(file_path)
        else:
            self._update_actions()

    def _open_item(self, item: QListWidgetItem) -> None:
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if isinstance(file_path, str):
            self.open_requested.emit(file_path)
        else:
            self._update_actions()
