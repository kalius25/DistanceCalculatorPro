"""
Distance Calculator Pro

Excel Table Model
Hiển thị dữ liệu Excel bằng QTableView.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import (
    QAbstractTableModel,
    QModelIndex,
    QPersistentModelIndex,
    Qt,
)
from PySide6.QtGui import QColor

from app.workbooks.virtual_reader import VirtualWorksheetDataSource

from .preview_row_status import PreviewRowStatus
from .virtual_table_cache import VirtualTableBlockCache


class ExcelTableModel(QAbstractTableModel):
    """QTableView model supporting both in-memory and lazy worksheet data."""

    def __init__(
        self,
        headers: list[str] | None = None,
        rows: list[list[Any]] | None = None,
        *,
        block_size: int = 256,
        max_cached_blocks: int = 5,
        show_status_column: bool = False,
    ) -> None:
        super().__init__()
        if block_size < 1:
            raise ValueError("block_size must be at least 1")

        self._headers = headers or []
        self._rows = rows or []
        self._source: VirtualWorksheetDataSource | None = None
        self._block_size = block_size
        self._cache = VirtualTableBlockCache(max_cached_blocks)
        self._show_status_column = show_status_column
        self._row_statuses: dict[int, PreviewRowStatus] = {}
        self._status_counts: dict[PreviewRowStatus, int] = {}

    # ==========================================================
    # Public
    # ==========================================================

    def set_data(
        self,
        headers: list[str],
        rows: list[list[Any]],
    ) -> None:
        """Switch to the legacy in-memory representation."""
        self.beginResetModel()
        self._replace_source(None)
        self._headers = list(headers)
        self._rows = [list(row) for row in rows]
        self._row_statuses.clear()
        self._status_counts.clear()
        self.endResetModel()

    def set_source(self, source: VirtualWorksheetDataSource) -> None:
        """Switch to a lazy worksheet source without materializing its rows."""
        self.beginResetModel()
        self._replace_source(source)
        self._headers = list(source.headers)
        self._rows = []
        self._row_statuses.clear()
        self._status_counts.clear()
        self.endResetModel()

    def clear_source(self) -> None:
        """Detach and close the current virtual source."""
        self.beginResetModel()
        self._replace_source(None)
        self._headers = []
        self._rows = []
        self._row_statuses.clear()
        self._status_counts.clear()
        self.endResetModel()

    def row_status(self, row: int) -> PreviewRowStatus:
        """Return the processing status for a zero-based data row."""
        if row < 0 or row >= self.rowCount():
            raise IndexError("Preview row is out of range.")
        return self._row_statuses.get(row, PreviewRowStatus.PENDING)

    def set_row_status(self, row: int, status: PreviewRowStatus) -> None:
        """Update one row status without resetting or reloading the grid."""
        if row < 0 or row >= self.rowCount():
            raise IndexError("Preview row is out of range.")
        if not isinstance(status, PreviewRowStatus):
            raise TypeError("status must be a PreviewRowStatus.")

        previous = self._row_statuses.get(row, PreviewRowStatus.PENDING)
        if previous is not status:
            if previous is not PreviewRowStatus.PENDING:
                remaining = self._status_counts.get(previous, 0) - 1
                if remaining > 0:
                    self._status_counts[previous] = remaining
                else:
                    self._status_counts.pop(previous, None)

            if status is PreviewRowStatus.PENDING:
                self._row_statuses.pop(row, None)
            else:
                self._row_statuses[row] = status
                self._status_counts[status] = self._status_counts.get(status, 0) + 1

        if self._show_status_column and self.columnCount() > 0:
            index = self.index(row, 0)
            self.dataChanged.emit(
                index,
                index,
                [
                    Qt.ItemDataRole.DisplayRole,
                    Qt.ItemDataRole.ForegroundRole,
                ],
            )

    def reset_row_statuses(self) -> None:
        """Return all tracked rows to the implicit Pending state."""
        if not self._row_statuses:
            return
        self._row_statuses.clear()
        self._status_counts.clear()
        if self._show_status_column and self.rowCount() > 0:
            self.dataChanged.emit(
                self.index(0, 0),
                self.index(self.rowCount() - 1, 0),
                [
                    Qt.ItemDataRole.DisplayRole,
                    Qt.ItemDataRole.ForegroundRole,
                ],
            )

    def status_count(self, status: PreviewRowStatus) -> int:
        """Return the number of rows currently in *status*."""
        if not isinstance(status, PreviewRowStatus):
            raise TypeError("status must be a PreviewRowStatus.")
        if status is PreviewRowStatus.PENDING:
            explicit = sum(self._status_counts.values())
            return max(self.rowCount() - explicit, 0)
        return self._status_counts.get(status, 0)

    def status_counts(self) -> dict[PreviewRowStatus, int]:
        """Return a snapshot of current row counts for every preview status."""
        return {status: self.status_count(status) for status in PreviewRowStatus}

    def invalidate_cache(self) -> None:
        """Discard lazy row blocks so subsequent reads are refreshed."""
        self._cache.clear()

    def clear(self) -> None:
        self.clear_source()

    # ==========================================================
    # Required
    # ==========================================================

    def rowCount(
        self,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        if self._source is not None:
            return self._source.row_count
        return len(self._rows)

    def columnCount(
        self,
        parent: QModelIndex | QPersistentModelIndex = QModelIndex(),
    ) -> int:
        data_columns = len(self._headers)
        if data_columns and self._show_status_column:
            return data_columns + 1
        return data_columns

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if not index.isValid():
            return None

        status_column = self._show_status_column and self.columnCount() > 0
        if status_column and index.column() == 0:
            status = self.row_status(index.row())
            if role == Qt.ItemDataRole.DisplayRole:
                return f"{status.symbol} {status.label}"
            if role == Qt.ItemDataRole.ForegroundRole:
                return self._status_color(status)
            if role == Qt.ItemDataRole.TextAlignmentRole:
                return Qt.AlignmentFlag.AlignCenter
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        data_column = index.column() - 1 if status_column else index.column()
        if self._source is not None:
            return self._virtual_value(index.row(), data_column)

        value = self._rows[index.row()][data_column]
        if value is None:
            return ""
        return str(value)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if self._show_status_column and self._headers:
                if section == 0:
                    return "Status"
                section -= 1
            if section < len(self._headers):
                return self._headers[section]

        return super().headerData(
            section,
            orientation,
            role,
        )

    @staticmethod
    def _status_color(status: PreviewRowStatus) -> QColor:
        colors = {
            PreviewRowStatus.PENDING: "#6B7280",
            PreviewRowStatus.RUNNING: "#2563EB",
            PreviewRowStatus.SUCCESS: "#16A34A",
            PreviewRowStatus.FAILED: "#DC2626",
            PreviewRowStatus.SKIPPED: "#CA8A04",
            PreviewRowStatus.INVALID: "#EA580C",
            PreviewRowStatus.RETRIED: "#2563EB",
        }
        return QColor(colors[status])

    # ==========================================================
    # Lazy source internals
    # ==========================================================

    def _virtual_value(self, row: int, column: int) -> str:
        source = self._source
        if source is None:
            return ""

        block_index = row // self._block_size
        rows = self._cache.get(block_index)
        if rows is None:
            rows = source.read_rows(
                block_index * self._block_size,
                self._block_size,
            )
            self._cache.put(block_index, rows)

        offset = row - (block_index * self._block_size)
        if offset >= len(rows) or column >= len(rows[offset]):
            return ""
        return rows[offset][column]

    def _replace_source(
        self,
        source: VirtualWorksheetDataSource | None,
    ) -> None:
        """Replace the current virtual source and discard cached row blocks."""
        self._close_source()
        self._cache.clear()
        self._source = source

    def _close_source(self) -> None:
        if self._source is not None:
            self._source.close()
            self._source = None


__all__ = ["ExcelTableModel"]
