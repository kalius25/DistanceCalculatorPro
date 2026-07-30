from PySide6.QtWidgets import QWidget

from .base_placeholder_page import BasePlaceholderPage


class SettingsPage(BasePlaceholderPage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            title="Settings",
            description=(
                "Application settings and provider preferences will be "
                "implemented later."
            ),
            parent=parent,
        )
