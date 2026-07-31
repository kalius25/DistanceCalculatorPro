"""Execution controls for a validated distance-calculation workspace."""

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class ExecutionCard(QFrame):
    """Present execution summary and Start/Stop controls."""

    start_requested = Signal()
    stop_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._running = False
        self.setObjectName("frmExecutionCard")
        self._create_widgets()
        self._create_layout()
        self._action_button.clicked.connect(self._on_action_clicked)
        self.reset()

    @property
    def running(self) -> bool:
        return self._running

    def set_summary(
        self,
        *,
        workbook_name: str,
        row_count: int,
        provider: str,
        travel_mode: str,
    ) -> None:
        """Update the immutable execution summary shown before starting."""
        self._workbook_value.setText(workbook_name or "—")
        self._rows_value.setText(f"{row_count:,}")
        self._provider_value.setText(provider or "—")
        self._travel_mode_value.setText(travel_mode.title() or "—")
        self._api_calls_value.setText(f"{row_count:,}")
        self._duration_value.setText(self._estimate_duration(row_count))

    def set_ready(self, ready: bool) -> None:
        """Enable Start only when the workspace is valid and idle."""
        if self._running:
            return
        self._action_button.setEnabled(ready)
        self._status_label.setText(
            "Ready to calculate."
            if ready
            else "Complete workspace configuration first."
        )
        self._status_label.setProperty("ready", ready)
        self._refresh_status_style()

    def set_running(self, running: bool) -> None:
        """Switch between Start and Stop presentation states."""
        self._running = running
        self._action_button.setText(
            "Stop Calculation" if running else "Start Calculation"
        )
        self._action_button.setObjectName(
            "btnStopCalculation" if running else "btnStartCalculation"
        )
        self._action_button.setEnabled(True)
        self._status_label.setText(
            "Calculation is running…" if running else "Ready to calculate."
        )
        self._status_label.setProperty("ready", not running)
        self._refresh_status_style()

    def reset(self) -> None:
        """Return the card to its initial disabled state."""
        self._running = False
        self._workbook_value.setText("—")
        self._rows_value.setText("0")
        self._provider_value.setText("—")
        self._travel_mode_value.setText("—")
        self._api_calls_value.setText("0")
        self._duration_value.setText("—")
        self._action_button.setText("Start Calculation")
        self._action_button.setObjectName("btnStartCalculation")
        self._action_button.setEnabled(False)
        self._status_label.setText("Complete workspace configuration first.")
        self._status_label.setProperty("ready", False)
        self._refresh_status_style()

    def _create_widgets(self) -> None:
        self._title_label = QLabel("Execution", self)
        self._title_label.setObjectName("lblSectionTitle")
        self._workbook_value = QLabel(self)
        self._rows_value = QLabel(self)
        self._provider_value = QLabel(self)
        self._travel_mode_value = QLabel(self)
        self._api_calls_value = QLabel(self)
        self._duration_value = QLabel(self)
        for value in (
            self._workbook_value,
            self._rows_value,
            self._provider_value,
            self._travel_mode_value,
            self._api_calls_value,
            self._duration_value,
        ):
            value.setObjectName("lblExecutionValue")
        self._action_button = QPushButton(self)
        self._status_label = QLabel(self)
        self._status_label.setObjectName("lblExecutionStatus")

    def _create_layout(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 10, 12, 12)
        layout.setSpacing(10)
        layout.addWidget(self._title_label)

        summary_layout = QGridLayout()
        summary_layout.setHorizontalSpacing(18)
        summary_layout.setVerticalSpacing(6)
        entries = (
            ("Workbook", self._workbook_value),
            ("Rows to calculate", self._rows_value),
            ("Provider", self._provider_value),
            ("Travel mode", self._travel_mode_value),
            ("Estimated API calls", self._api_calls_value),
            ("Estimated duration", self._duration_value),
        )
        for row, (caption, value) in enumerate(entries):
            caption_label = QLabel(caption, self)
            caption_label.setObjectName("lblInspectorCaption")
            summary_layout.addWidget(caption_label, row, 0)
            summary_layout.addWidget(value, row, 1)
        summary_layout.setColumnStretch(1, 1)
        layout.addLayout(summary_layout)
        layout.addWidget(self._action_button)
        layout.addWidget(self._status_label)

    def _on_action_clicked(self) -> None:
        if self._running:
            self.stop_requested.emit()
        else:
            self.start_requested.emit()

    @staticmethod
    def _estimate_duration(row_count: int) -> str:
        if row_count <= 0:
            return "—"
        minutes = max(1, round(row_count * 0.2 / 60))
        return f"≈ {minutes:,} min"

    def _refresh_status_style(self) -> None:
        self._status_label.style().unpolish(self._status_label)
        self._status_label.style().polish(self._status_label)
