from PySide6.QtCore import QModelIndex
from PySide6.QtCore import Qt

from app.models.excel_table_model import ExcelTableModel


def test_constructor():
    model = ExcelTableModel()

    assert model.rowCount() == 0
    assert model.columnCount() == 0


def test_constructor_with_data():
    model = ExcelTableModel(
        ["A", "B"],
        [[1, 2], [3, 4]],
    )

    assert model.rowCount() == 2
    assert model.columnCount() == 2


def test_set_data():
    model = ExcelTableModel()

    model.set_data(
        ["Col1", "Col2"],
        [["A", "B"]],
    )

    assert model.rowCount() == 1
    assert model.columnCount() == 2


def test_clear():
    model = ExcelTableModel(
        ["A"],
        [[1]],
    )

    model.clear()

    assert model.rowCount() == 0
    assert model.columnCount() == 0


def test_data_display():
    model = ExcelTableModel(
        ["A"],
        [[123]],
    )

    index = model.index(0, 0)

    assert model.data(index) == "123"


def test_data_none():
    model = ExcelTableModel(
        ["A"],
        [[None]],
    )

    index = model.index(0, 0)

    assert model.data(index) == ""


def test_data_invalid_index():
    model = ExcelTableModel()

    assert model.data(QModelIndex()) is None


def test_data_wrong_role():
    model = ExcelTableModel(
        ["A"],
        [[1]],
    )

    index = model.index(0, 0)

    assert model.data(
        index,
        Qt.ItemDataRole.EditRole,
    ) is None


def test_header_horizontal():
    model = ExcelTableModel(
        ["Name", "Age"],
        [],
    )

    assert (
        model.headerData(
            1,
            Qt.Orientation.Horizontal,
        )
        == "Age"
    )


def test_header_horizontal_out_of_range():
    model = ExcelTableModel(
        ["Name"],
        [],
    )

    assert (
        model.headerData(
            5,
            Qt.Orientation.Horizontal,
        )
        == super(ExcelTableModel, model).headerData(
            5,
            Qt.Orientation.Horizontal,
        )
    )


def test_header_vertical():
    model = ExcelTableModel(
        ["A"],
        [[1]],
    )

    assert (
        model.headerData(
            0,
            Qt.Orientation.Vertical,
        )
        == super(ExcelTableModel, model).headerData(
            0,
            Qt.Orientation.Vertical,
        )
    )


def test_header_wrong_role():
    model = ExcelTableModel(
        ["A"],
        [[1]],
    )

    assert (
        model.headerData(
            0,
            Qt.Orientation.Horizontal,
            Qt.ItemDataRole.EditRole,
        )
        is None
    )