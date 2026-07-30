from PySide6.QtWidgets import QWidget

from .base_placeholder_page import BasePlaceholderPage


class AboutPage(BasePlaceholderPage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            title="About",
            description="DistanceCalculatorPro application information.",
            parent=parent,
        )
