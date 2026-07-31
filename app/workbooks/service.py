from datetime import datetime
from pathlib import Path

from .models import WorkbookInfo
from .readers import WorkbookReader


class UnsupportedWorkbookError(ValueError):
    """Raised when no configured reader supports the selected file."""


class WorkbookInspectorService:
    """Select the correct reader and compose immutable workbook metadata."""

    def __init__(self, readers: tuple[WorkbookReader, ...]) -> None:
        self._readers = readers

    def inspect(self, file_path: str) -> WorkbookInfo:
        path = Path(file_path)
        if not path.is_file():
            raise FileNotFoundError(f"Workbook not found: {path}")

        reader = next(
            (candidate for candidate in self._readers if candidate.supports(path)),
            None,
        )
        if reader is None:
            raise UnsupportedWorkbookError(
                f"Unsupported workbook format: {path.suffix.lower()}"
            )

        stat = path.stat()
        return WorkbookInfo(
            file_path=str(path),
            file_name=path.name,
            file_type=path.suffix.lower().lstrip(".").upper(),
            file_size_bytes=stat.st_size,
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            worksheets=reader.read_worksheets(path),
        )
