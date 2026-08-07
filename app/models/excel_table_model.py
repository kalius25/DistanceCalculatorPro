"""
Distance Calculator Pro

Excel Table Model
Hiển thị dữ liệu Excel bằng QTableView.
"""

from __future__ import annotations

from typing import Any

from PySide6.QtCore import QAbstractTableModel, QModelIndex, QPersistentModelIndex, Qt

from app.workbooks.virtual_reader import VirtualWorksheetDataSource

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
    ) -> None:
        super().__init__()
        if block_size < 1:
            raise ValueError("block_size must be at least 1")

        self._headers = headers or []
        self._rows = rows or []
        self._source: VirtualWorksheetDataSource | None = None
        self._block_size = block_size
        self._cache = VirtualTableBlockCache(max_cached_blocks)

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
        self._close_source()
        self._headers = headers
        self._rows = rows
        self._cache.clear()
        self.endResetModel()

    def set_source(self, source: VirtualWorksheetDataSource) -> None:
        """Switch to a lazy worksheet source without materializing its rows."""
        self.beginResetModel()
        self._close_source()
        self._source = source
        self._headers = list(source.headers)
        self._rows = []
        self._cache.clear()
        self.endResetModel()

    def clear_source(self) -> None:
        """Detach and close the current virtual source."""
        self.beginResetModel()
        self._close_source()
        self._headers = []
        self._rows = []
        self._cache.clear()
        self.endResetModel()

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
        return len(self._headers)

    def data(
        self,
        index: QModelIndex | QPersistentModelIndex,
        role: int = Qt.ItemDataRole.DisplayRole,
    ):
        if not index.isValid():
            return None

        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if self._source is not None:
            return self._virtual_value(index.row(), index.column())

        value = self._rows[index.row()][index.column()]
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
            if section < len(self._headers):
                return self._headers[section]

        return super().headerData(
            section,
            orientation,
            role,
        )

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

    def _close_source(self) -> None:
        if self._source is not None:
            self._source.close()
            self._source = None


__all__ = ["ExcelTableModel"]
