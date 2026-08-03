"""Compose workbook reading, row mapping, and queue creation."""

from __future__ import annotations

from pathlib import Path

from app.presentation.workspace_configuration import WorkspaceConfiguration

from .batch_queue import BatchQueue
from .row_mapper import RowMapper
from .workbook_reader import WorkbookReader


class QueueBuilder:
    """Build a state-aware batch queue from one workbook worksheet."""

    def __init__(
        self,
        reader: WorkbookReader | None = None,
        mapper: RowMapper | None = None,
    ) -> None:
        self._reader = reader or WorkbookReader()
        self._mapper = mapper or RowMapper()

    def build(
        self,
        file_path: str | Path,
        sheet_name: str,
        configuration: WorkspaceConfiguration,
    ) -> BatchQueue:
        stream = self._reader.read(file_path, sheet_name)
        indexes = self._mapper.resolve_indexes(stream.headers, configuration)
        jobs = (
            self._mapper.map_row(row, indexes, configuration) for row in stream.rows
        )
        return BatchQueue(jobs)
