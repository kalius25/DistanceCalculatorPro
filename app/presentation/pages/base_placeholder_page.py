from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class BasePlaceholderPage(QWidget):
    """Base page used during the presentation foundation sprint."""

    def __init__(
        self,
        title: str,
        description: str,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._title = title
        self._description = description
        self._create_layout()

    def _create_layout(self) -> None:
        title_label = QLabel(self._title)
        title_label.setObjectName("lblPageTitle")

        description_label = QLabel(self._description)
        description_label.setObjectName("lblPageDescription")
        description_label.setWordWrap(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(8)
        layout.addWidget(title_label)
        layout.addWidget(description_label)
        layout.addStretch()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
