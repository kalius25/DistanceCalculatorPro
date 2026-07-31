from pathlib import Path
from unittest.mock import MagicMock

import pytest
from openpyxl import Workbook

from app.workbooks import (
    CsvWorkbookReader,
    OpenPyXLWorkbookReader,
    UnsupportedWorkbookError,
    WorkbookInspectorService,
    WorksheetInfo,
)


def test_csv_reader_streams_dimensions_and_headers(tmp_path: Path) -> None:
    path = tmp_path / "routes.csv"
    path.write_text("Origin,Destination,Note\nA,B\nC,D,Fast\n", encoding="utf-8")
    reader = CsvWorkbookReader()

    sheets = reader.read_worksheets(path)

    assert reader.supports(path)
    assert sheets == (
        WorksheetInfo(
            "routes",
            3,
            3,
            ("Origin", "Destination", "Note"),
            (("A", "B"), ("C", "D", "Fast")),
        ),
    )


def test_csv_reader_handles_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "empty.csv"
    path.touch()

    assert CsvWorkbookReader().read_worksheets(path) == (
        WorksheetInfo("empty", 0, 0, ()),
    )


def test_excel_reader_reads_multiple_sheet_metadata(tmp_path: Path) -> None:
    path = tmp_path / "routes.xlsx"
    workbook = Workbook()
    active = workbook.active
    active.title = "Routes"
    active.append(["Origin", "Destination"])
    active.append(["A", "B"])
    second = workbook.create_sheet("Settings")
    second.append(["Provider"])
    workbook.save(path)

    sheets = OpenPyXLWorkbookReader().read_worksheets(path)

    assert sheets[0] == WorksheetInfo(
        "Routes", 2, 2, ("Origin", "Destination"), (("A", "B"),)
    )
    assert sheets[1] == WorksheetInfo("Settings", 1, 1, ("Provider",))


def test_service_selects_reader_and_composes_file_metadata(tmp_path: Path) -> None:
    path = tmp_path / "routes.csv"
    path.write_text("A,B\n1,2\n", encoding="utf-8")
    reader = MagicMock()
    reader.supports.return_value = True
    reader.read_worksheets.return_value = (WorksheetInfo("routes", 2, 2, ("A", "B")),)

    result = WorkbookInspectorService((reader,)).inspect(str(path))

    reader.supports.assert_called_once_with(path)
    reader.read_worksheets.assert_called_once_with(path)
    assert result.file_name == "routes.csv"
    assert result.file_type == "CSV"
    assert result.file_size_bytes == path.stat().st_size
    assert result.worksheets[0].row_count == 2


def test_service_rejects_missing_and_unsupported_files(tmp_path: Path) -> None:
    service = WorkbookInspectorService(())
    with pytest.raises(FileNotFoundError, match="Workbook not found"):
        service.inspect(str(tmp_path / "missing.xlsx"))

    path = tmp_path / "routes.txt"
    path.touch()
    with pytest.raises(UnsupportedWorkbookError, match="Unsupported workbook format"):
        service.inspect(str(path))


def test_excel_reader_supports_xlsm_case_insensitively(tmp_path: Path) -> None:
    reader = OpenPyXLWorkbookReader()

    assert reader.supports(tmp_path / "book.XLSM")
    assert not reader.supports(tmp_path / "book.csv")


def test_csv_reader_stops_retaining_preview_after_limit(tmp_path: Path) -> None:
    path = tmp_path / "large.csv"
    rows = ["A,B"] + [f"{index},{index + 1}" for index in range(501)]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")

    sheet = CsvWorkbookReader().read_worksheets(path)[0]

    assert sheet.row_count == 502
    assert len(sheet.preview_rows) == CsvWorkbookReader.PREVIEW_ROW_LIMIT
