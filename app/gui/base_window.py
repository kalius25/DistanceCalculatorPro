"""Base window for all application windows.

Sprint 01A placeholder.
"""

from PySide6.QtWidgets import QMainWindow


class BaseWindow(QMainWindow):
    """Common functionality shared by application windows."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
