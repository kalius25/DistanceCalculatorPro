from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class WorksheetInfo:
    """Lightweight metadata and bounded preview for one worksheet."""

    name: str
    row_count: int
    column_count: int
    headers: tuple[str, ...]
    preview_rows: tuple[tuple[str, ...], ...] = ()


@dataclass(frozen=True, slots=True)
class WorkbookInfo:
    """Metadata required by the workbook inspector UI."""

    file_path: str
    file_name: str
    file_type: str
    file_size_bytes: int
    modified_at: datetime
    worksheets: tuple[WorksheetInfo, ...]
