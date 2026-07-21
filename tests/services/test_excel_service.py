from unittest.mock import MagicMock, patch

import pytest

from app.services.excel_service import ExcelService


# ==========================================================
# Constructor
# ==========================================================

def test_init():
    service = ExcelService()

    assert service.file_path is None
    assert service.workbook is None


# ==========================================================
# Workbook
# ==========================================================

@patch("app.services.excel_service.load_workbook")
def test_open_workbook(mock_load):
    workbook = MagicMock()
    workbook.sheetnames = ["Sheet1", "Sheet2"]

    mock_load.return_value = workbook

    service = ExcelService()

    result = service.open_workbook("sample.xlsx")

    assert result == ["Sheet1", "Sheet2"]
    assert service.workbook is workbook
    mock_load.assert_called_once()


def test_get_sheet_names_without_workbook():
    service = ExcelService()

    assert service.get_sheet_names() == []


def test_get_sheet_names():
    workbook = MagicMock()
    workbook.sheetnames = ["A", "B"]

    service = ExcelService()
    service.workbook = workbook

    assert service.get_sheet_names() == ["A", "B"]


# ==========================================================
# Worksheet
# ==========================================================

def test_get_worksheet_without_workbook():
    service = ExcelService()

    with pytest.raises(RuntimeError):
        service.get_worksheet("Sheet1")


def test_get_worksheet():
    workbook = MagicMock()
    worksheet = MagicMock()

    workbook.__getitem__.return_value = worksheet

    service = ExcelService()
    service.workbook = workbook

    assert service.get_worksheet("Sheet1") is worksheet
    workbook.__getitem__.assert_called_once_with("Sheet1")


# ==========================================================
# Header
# ==========================================================

def test_read_headers():
    worksheet = MagicMock()

    worksheet.iter_rows.return_value = iter([
        ("Name", None, 123)
    ])

    service = ExcelService()
    service.get_worksheet = MagicMock(return_value=worksheet)

    headers = service.read_headers("Sheet1")

    assert headers == ["Name", "", "123"]


# ==========================================================
# Preview
# ==========================================================

def test_read_preview():
    worksheet = MagicMock()

    worksheet.iter_rows.return_value = iter([
        ("A", None, 1),
        ("B", 2, None),
    ])

    service = ExcelService()
    service.get_worksheet = MagicMock(return_value=worksheet)

    rows = service.read_preview("Sheet1")

    assert rows == [
        ["A", "", 1],
        ["B", 2, ""],
    ]


def test_read_preview_empty():
    worksheet = MagicMock()

    worksheet.iter_rows.return_value = iter([])

    service = ExcelService()
    service.get_worksheet = MagicMock(return_value=worksheet)

    assert service.read_preview("Sheet1") == []


# ==========================================================
# Read All
# ==========================================================

def test_read_all():
    worksheet = MagicMock()

    worksheet.iter_rows.return_value = iter([
        ("A", None),
        (None, "B"),
    ])

    service = ExcelService()
    service.get_worksheet = MagicMock(return_value=worksheet)

    rows = service.read_all("Sheet1")

    assert rows == [
        ["A", ""],
        ["", "B"],
    ]


def test_read_all_empty():
    worksheet = MagicMock()

    worksheet.iter_rows.return_value = iter([])

    service = ExcelService()
    service.get_worksheet = MagicMock(return_value=worksheet)

    assert service.read_all("Sheet1") == []