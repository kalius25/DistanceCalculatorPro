from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from ..app_metadata import AppMetadata


class AboutDialog(QDialog):
    """Displays application identity and current release information."""

    def __init__(
        self,
        metadata: AppMetadata,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._metadata = metadata
        self._create_widgets()
        self._create_layout()
        self._connect_signals()
        self._apply_initial_state()

    def _create_widgets(self) -> None:
        self._title_label = QLabel(self._metadata.name, self)
        self._title_label.setObjectName("lblAboutTitle")

        self._version_label = QLabel(
            f"Version {self._metadata.version}",
            self,
        )
        self._description_label = QLabel(
            "Desktop workspace for batch route-distance calculation.",
            self,
        )
        self._description_label.setWordWrap(True)
        self._description_label.setAlignment(
            Qt.AlignmentFlag.AlignCenter,
        )

        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok,
            parent=self,
        )

    def _create_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(self._title_label)
        layout.addWidget(self._version_label)
        layout.addWidget(self._description_label)
        layout.addSpacing(8)
        layout.addWidget(self._button_box)

    def _connect_signals(self) -> None:
        self._button_box.accepted.connect(self.accept)

    def _apply_initial_state(self) -> None:
        self.setWindowTitle(f"About {self._metadata.name}")
        self.setModal(True)
        self.setMinimumWidth(420)
