from PySide6.QtCore import QModelIndex, Qt

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

    assert (
        model.data(
            index,
            Qt.ItemDataRole.EditRole,
        )
        is None
    )


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

    assert model.headerData(
        5,
        Qt.Orientation.Horizontal,
    ) == super(ExcelTableModel, model).headerData(
        5,
        Qt.Orientation.Horizontal,
    )


def test_header_vertical():
    model = ExcelTableModel(
        ["A"],
        [[1]],
    )

    assert model.headerData(
        0,
        Qt.Orientation.Vertical,
    ) == super(ExcelTableModel, model).headerData(
        0,
        Qt.Orientation.Vertical,
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


class FakeVirtualSource:
    def __init__(self) -> None:
        from pathlib import Path

        self.file_path = Path("routes.xlsx")
        self.worksheet_name = "Routes"
        self.headers = ("Origin", "Destination")
        self.row_count = 6
        self.column_count = 2
        self.read_calls: list[tuple[int, int]] = []
        self.closed = False

    def read_rows(self, start: int, count: int) -> tuple[tuple[str, ...], ...]:
        self.read_calls.append((start, count))
        stop = min(start + count, self.row_count)
        return tuple((f"O{row}", f"D{row}") for row in range(start, stop))

    def close(self) -> None:
        self.closed = True


def test_constructor_rejects_invalid_virtual_block_size():
    import pytest

    with pytest.raises(ValueError, match="block_size"):
        ExcelTableModel(block_size=0)


def test_virtual_source_exposes_full_dimensions_and_loads_blocks_lazily():
    source = FakeVirtualSource()
    model = ExcelTableModel(block_size=2, max_cached_blocks=2)

    model.set_source(source)

    assert model.rowCount() == 6
    assert model.columnCount() == 2
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Origin"
    assert source.read_calls == []

    assert model.data(model.index(3, 1)) == "D3"
    assert source.read_calls == [(2, 2)]

    assert model.data(model.index(2, 0)) == "O2"
    assert source.read_calls == [(2, 2)]

    assert model.data(model.index(0, 0)) == "O0"
    assert source.read_calls == [(2, 2), (0, 2)]


def test_invalidate_cache_forces_virtual_block_reload():
    source = FakeVirtualSource()
    model = ExcelTableModel(block_size=2)
    model.set_source(source)

    assert model.data(model.index(0, 0)) == "O0"
    model.invalidate_cache()
    assert model.data(model.index(0, 0)) == "O0"

    assert source.read_calls == [(0, 2), (0, 2)]


def test_replacing_virtual_source_closes_previous_source():
    first = FakeVirtualSource()
    second = FakeVirtualSource()
    model = ExcelTableModel()

    model.set_source(first)
    model.set_source(second)

    assert first.closed
    assert not second.closed

    model.clear_source()
    assert second.closed
    assert model.rowCount() == 0
    assert model.columnCount() == 0


def test_set_data_closes_virtual_source_and_returns_to_memory_rows():
    source = FakeVirtualSource()
    model = ExcelTableModel()
    model.set_source(source)

    model.set_data(["A"], [[None]])

    assert source.closed
    assert model.rowCount() == 1
    assert model.data(model.index(0, 0)) == ""


def test_virtual_value_is_empty_for_short_source_block():
    source = FakeVirtualSource()
    source.row_count = 2

    def short_rows(start: int, count: int) -> tuple[tuple[str, ...], ...]:
        source.read_calls.append((start, count))
        return (("only-one-column",),)

    source.read_rows = short_rows  # type: ignore[method-assign]
    model = ExcelTableModel(block_size=2)
    model.set_source(source)

    assert model.data(model.index(0, 1)) == ""
    assert model.data(model.index(1, 0)) == ""


def test_virtual_value_without_source_is_empty():
    model = ExcelTableModel()

    assert model._virtual_value(0, 0) == ""
