"""Status-aware filtering for the Data Preview grid."""

from __future__ import annotations

from PySide6.QtCore import (
    QModelIndex,
    QPersistentModelIndex,
    QSortFilterProxyModel,
)

from .excel_table_model import ExcelTableModel
from .preview_row_status import PreviewRowStatus


class PreviewStatusFilterProxyModel(QSortFilterProxyModel):
    """Filter preview rows by one or more processing statuses."""

    def __init__(self) -> None:
        super().__init__()
        self._statuses: frozenset[PreviewRowStatus] | None = None
        self.setDynamicSortFilter(True)

    @property
    def statuses(self) -> frozenset[PreviewRowStatus] | None:
        """Return the active status filter, or ``None`` for all rows."""
        return self._statuses

    def set_statuses(
        self,
        statuses: set[PreviewRowStatus] | frozenset[PreviewRowStatus] | None,
    ) -> None:
        """Show only rows matching *statuses*; ``None`` shows every row."""
        normalized = None if statuses is None else frozenset(statuses)
        if normalized == self._statuses:
            return
        self._statuses = normalized
        self.beginFilterChange()
        self.endFilterChange()

    def filterAcceptsRow(
        self,
        source_row: int,
        source_parent: QModelIndex | QPersistentModelIndex,
    ) -> bool:
        if self._statuses is None:
            return True
        source = self.sourceModel()
        if not isinstance(source, ExcelTableModel):
            return True
        return source.row_status(source_row) in self._statuses

    def refresh_filter(self) -> None:
        """Re-evaluate the active filter after source row statuses change."""
        self.beginFilterChange()
        self.endFilterChange()


__all__ = ["PreviewStatusFilterProxyModel"]
