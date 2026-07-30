from PySide6.QtWidgets import QWidget

from .base_placeholder_page import BasePlaceholderPage


class HistoryPage(BasePlaceholderPage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            title="History",
            description="Calculation history will be implemented in a later sprint.",
            parent=parent,
        )
