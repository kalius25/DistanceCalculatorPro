from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from ..app_metadata import AppMetadata


class AboutPage(QWidget):
    """Application identity and release information."""

    details_requested = Signal()

    def __init__(
        self,
        metadata: AppMetadata | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._metadata = metadata or AppMetadata()
        self._create_layout()

    def _create_layout(self) -> None:
        title = QLabel("About")
        title.setObjectName("lblPageTitle")

        description = QLabel(
            "DistanceCalculatorPro application and release information."
        )
        description.setObjectName("lblPageDescription")
        description.setWordWrap(True)

        product = QLabel(self._metadata.name)
        product.setObjectName("lblAboutPageProduct")

        version = QLabel(f"Version {self._metadata.version}")
        version.setObjectName("lblAboutPageVersion")

        release = QLabel("Release channel: v1.2 · Stable")
        release.setObjectName("lblAboutPageRelease")

        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("frmAboutPageSeparator")

        summary = QLabel(
            "Desktop workspace for reliable batch route-distance calculation "
            "and logistics analysis."
        )
        summary.setObjectName("lblAboutPageSummary")
        summary.setWordWrap(True)

        organization = QLabel(f"Organization: {self._metadata.organization}")
        organization.setObjectName("lblAboutPageOrganization")

        self._details_button = QPushButton("About dialog")
        self._details_button.setObjectName("btnAboutDialog")
        self._details_button.clicked.connect(self.details_requested.emit)

        buttons = QHBoxLayout()
        buttons.addWidget(self._details_button)
        buttons.addStretch()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)
        layout.addWidget(title)
        layout.addWidget(description)
        layout.addSpacing(8)
        layout.addWidget(product)
        layout.addWidget(version)
        layout.addWidget(release)
        layout.addWidget(separator)
        layout.addWidget(summary)
        layout.addWidget(organization)
        layout.addStretch()
        layout.addLayout(buttons)
