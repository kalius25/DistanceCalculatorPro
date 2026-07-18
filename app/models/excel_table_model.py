"""
Distance Calculator Pro

Excel Table Model
Hiển thị dữ liệu Excel bằng QTableView.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel
from PySide6.QtCore import QModelIndex
from PySide6.QtCore import Qt


class ExcelTableModel(QAbstractTableModel):
    """
    Model dữ liệu cho QTableView.
    """

    def __init__(
        self,
        headers: list[str] | None = None,
        rows: list[list[Any]] | None = None,
    ) -> None:

        super().__init__()

        self._headers = headers or []
        self._rows = rows or []

    # ==========================================================
    # Public
    # ==========================================================

    def set_data(
        self,
        headers: list[str],
        rows: list[list[Any]],
    ) -> None:

        self.beginResetModel()

        self._headers = headers
        self._rows = rows

        self.endResetModel()

    def clear(self) -> None:

        self.beginResetModel()

        self._headers = []
        self._rows = []

        self.endResetModel()

    # ==========================================================
    # Required
    # ==========================================================

    def rowCount(
        self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:

        return len(self._rows)

    def columnCount(
        self,
        parent: QModelIndex = QModelIndex(),
    ) -> int:

        return len(self._headers)

    def data(
        self,
        index: QModelIndex,
        role: int = Qt.DisplayRole,
    ):

        if not index.isValid():
            return None

        if role != Qt.DisplayRole:
            return None

        value = self._rows[index.row()][index.column()]

        if value is None:
            return ""

        return str(value)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.DisplayRole,
    ):

        if role != Qt.DisplayRole:
            return None

        if orientation == Qt.Horizontal:

            if section < len(self._headers):
                return self._headers[section]

        return super().headerData(
            section,
            orientation,
            role,
        )