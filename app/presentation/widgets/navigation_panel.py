from PySide6.QtCore import Signal
from PySide6.QtWidgets import QListWidget, QListWidgetItem, QWidget


class NavigationPanel(QListWidget):
    """Primary application navigation."""

    page_changed = Signal(int)

    _ITEMS = (
        ("Home", "home"),
        ("History", "history"),
        ("Settings", "settings"),
        ("About", "about"),
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("lstNavigation")
        self.setFixedWidth(190)
        self._populate_items()
        self.currentRowChanged.connect(self.page_changed.emit)
        self.setCurrentRow(0)

    def _populate_items(self) -> None:
        for label, page_key in self._ITEMS:
            item = QListWidgetItem(label)
            item.setData(256, page_key)
            self.addItem(item)
