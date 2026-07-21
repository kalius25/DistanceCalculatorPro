"""Batch window.

Sprint 01A placeholder.
"""

from .base_window import BaseWindow


class BatchWindow(BaseWindow):
    """Batch processing window."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Batch Distance Calculator")
