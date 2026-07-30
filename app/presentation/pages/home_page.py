from PySide6.QtWidgets import QWidget

from .base_placeholder_page import BasePlaceholderPage


class HomePage(BasePlaceholderPage):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(
            title="Home",
            description=(
                "Batch distance calculation workspace will be implemented "
                "in Sprint 1B."
            ),
            parent=parent,
        )
