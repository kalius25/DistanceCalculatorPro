from collections.abc import Generator
from pathlib import Path
from shutil import copyfile
from typing import cast
from unittest.mock import MagicMock, patch
from zipfile import BadZipFile

import pytest

from app.batch import BatchWorkbookError
from app.batch.models import WorkbookRow
from app.batch.workbook_reader import WorkbookReader

FIXTURE_DIRECTORY = Path(__file__).parent.parent / "fixtures"

def test_excel_reader_streams_rows_and_closes_after_iteration(
    tmp_path: Path,
) -> None:
    source_path = FIXTURE_DIRECTORY / "routes.xlsx"
    path = tmp_path / "routes.xlsx"

    copyfile(source_path, path)

    stream = WorkbookReader().read(path, "Routes")

    assert stream.headers == (
        "Origin",
        "Destination",
        "",
    )
    assert [
        (row.row_number, row.values)
        for row in stream.rows
    ] == [
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

    with pytest.raises(
        FileNotFoundError,
        match="Workbook not found",
    ):
        reader.read(
            tmp_path / "missing.xlsx",
            "Routes",
        )

    unsupported = tmp_path / "routes.txt"
    unsupported.touch()

    with pytest.raises(
        BatchWorkbookError,
        match="Unsupported workbook type",
    ):
        reader.read(
            unsupported,
            "Routes",
        )

    excel_path = tmp_path / "routes.xlsx"
    excel_path.touch()

    workbook = MagicMock()
    workbook.sheetnames = ["Routes"]

    with patch(
        "app.batch.workbook_reader.load_workbook",
        return_value=workbook,
    ) as load_workbook_mock:
        with pytest.raises(
            BatchWorkbookError,
            match="Worksheet not found: Missing",
        ):
            reader.read(
                excel_path,
                "Missing",
            )

    load_workbook_mock.assert_called_once_with(
        filename=excel_path,
        read_only=True,
        data_only=True,
        keep_links=False,
    )
    workbook.close.assert_called_once_with()

def test_excel_reader_closes_source_when_workbook_is_invalid(
    tmp_path: Path,
) -> None:
    path = tmp_path / "invalid.xlsx"
    path.write_bytes(b"not a valid Excel workbook")

    reader = WorkbookReader()

    with pytest.raises(BadZipFile):
        reader.read(
            path,
            "Routes",
        )

def test_excel_stream_can_be_closed_before_full_iteration(
    tmp_path: Path,
) -> None:
    path = tmp_path / "routes.xlsx"
    copyfile(FIXTURE_DIRECTORY / "routes.xlsx", path)

    stream = WorkbookReader().read(
        path,
        "Routes",
    )

    rows = cast(
        Generator[WorkbookRow, None, None],
        stream.rows,
    )

    first_row = next(rows)

    assert first_row.row_number == 2

    rows.close()

class _UnprintableHeader:
    def __str__(self) -> str:
        raise RuntimeError("header conversion failed")


def test_excel_reader_closes_iterator_when_header_conversion_fails(
    tmp_path: Path,
) -> None:
    path = tmp_path / "routes.xlsx"
    path.touch()

    iterator = MagicMock()
    iterator.__next__.side_effect = [(_UnprintableHeader(),)]

    worksheet = MagicMock()
    worksheet.iter_rows.return_value = iterator

    workbook = MagicMock()
    workbook.sheetnames = ["Routes"]
    workbook.__getitem__.return_value = worksheet

    with patch(
        "app.batch.workbook_reader.load_workbook",
        return_value=workbook,
    ):
        with pytest.raises(RuntimeError, match="header conversion failed"):
            WorkbookReader().read(path, "Routes")

    iterator.close.assert_called_once_with()
    workbook.close.assert_called_once_with()


def test_excel_reader_supports_iterator_without_close(
    tmp_path: Path,
) -> None:
    path = tmp_path / "routes.xlsx"
    path.touch()

    iterator = iter(
        [
            ("Origin", "Destination"),
            ("A", "B"),
        ]
    )

    worksheet = MagicMock()
    worksheet.iter_rows.return_value = iterator

    workbook = MagicMock()
    workbook.sheetnames = ["Routes"]
    workbook.__getitem__.return_value = worksheet

    with patch(
        "app.batch.workbook_reader.load_workbook",
        return_value=workbook,
    ):
        stream = WorkbookReader().read(path, "Routes")
        rows = list(stream.rows)

    assert stream.headers == ("Origin", "Destination")
    assert [(row.row_number, row.values) for row in rows] == [
        (2, ("A", "B")),
    ]
    workbook.close.assert_called_once_with()

def test_excel_reader_handles_non_closable_iterator_during_header_error(
    tmp_path: Path,
) -> None:
    class NonClosableIterator:
        def __iter__(self):
            return self

        def __next__(self):
            return (_UnprintableHeader(),)

    path = tmp_path / "routes.xlsx"
    path.touch()

    iterator = NonClosableIterator()

    worksheet = MagicMock()
    worksheet.iter_rows.return_value = iterator

    workbook = MagicMock()
    workbook.sheetnames = ["Routes"]
    workbook.__getitem__.return_value = worksheet

    with patch(
        "app.batch.workbook_reader.load_workbook",
        return_value=workbook,
    ):
        with pytest.raises(
            RuntimeError,
            match="header conversion failed",
        ):
            WorkbookReader().read(
                path,
                "Routes",
            )

    workbook.close.assert_called_once_with()