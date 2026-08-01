from pathlib import Path

import pytest
from openpyxl import Workbook

from app.batch import BatchWorkbookError, WorkbookReader


def test_excel_reader_streams_rows_and_closes_after_iteration(tmp_path: Path) -> None:
    path = tmp_path / "routes.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Routes"
    sheet.append(["Origin", "Destination", None])
    sheet.append(["A", "B", None])
    sheet.append(["C", "D", 12])
    workbook.save(path)

    stream = WorkbookReader().read(path, "Routes")

    assert stream.headers == ("Origin", "Destination", "")
    assert [(row.row_number, row.values) for row in stream.rows] == [
        (2, ("A", "B", None)),
        (3, ("C", "D", 12)),
    ]


def test_csv_reader_streams_rows_and_supports_empty_file(tmp_path: Path) -> None:
    path = tmp_path / "routes.csv"
    path.write_text(
        "Origin,Destination,Distance\nA,B,\nC,D,4\n",
        encoding="utf-8",
    )

    stream = WorkbookReader().read(path, "ignored")

    assert stream.headers == ("Origin", "Destination", "Distance")
    assert [row.row_number for row in stream.rows] == [2, 3]

    empty = tmp_path / "empty.csv"
    empty.touch()
    empty_stream = WorkbookReader().read(empty, "ignored")
    assert empty_stream.headers == ()
    assert list(empty_stream.rows) == []


def test_reader_rejects_missing_unsupported_and_unknown_sheet(
    tmp_path: Path,
) -> None:
    reader = WorkbookReader()
    with pytest.raises(FileNotFoundError, match="Workbook not found"):
        reader.read(tmp_path / "missing.xlsx", "Routes")

    unsupported = tmp_path / "routes.txt"
    unsupported.touch()
    with pytest.raises(BatchWorkbookError, match="Unsupported workbook type"):
        reader.read(unsupported, "Routes")

    path = tmp_path / "routes.xlsx"
    Workbook().save(path)
    with pytest.raises(BatchWorkbookError, match="Worksheet not found"):
        reader.read(path, "Missing")
