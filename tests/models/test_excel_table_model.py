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
    model = ExcelTableModel(block_size=2, max_cached_blocks=2)

    model.set_source(first)
    assert model.data(model.index(0, 0)) == "O0"
    assert first.read_calls == [(0, 2)]

    model.set_source(second)

    assert first.closed
    assert not second.closed
    assert model.data(model.index(0, 0)) == "O0"
    assert second.read_calls == [(0, 2)]

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


def test_status_column_is_opt_in_and_shifts_data_columns():
    from app.models.preview_row_status import PreviewRowStatus

    model = ExcelTableModel(
        ["Origin", "Destination"],
        [["A", "B"]],
        show_status_column=True,
    )

    assert model.columnCount() == 3
    assert model.headerData(0, Qt.Orientation.Horizontal) == "Status"
    assert model.headerData(1, Qt.Orientation.Horizontal) == "Origin"
    assert model.data(model.index(0, 0)) == "○ Pending"
    assert model.data(model.index(0, 1)) == "A"
    assert model.row_status(0) is PreviewRowStatus.PENDING


def test_status_column_supports_all_visual_states_and_roles():
    from PySide6.QtGui import QColor

    from app.models.preview_row_status import PreviewRowStatus

    model = ExcelTableModel(["A"], [[1]], show_status_column=True)
    index = model.index(0, 0)

    expected = (
        (PreviewRowStatus.PENDING, "○ Pending", "#6b7280"),
        (PreviewRowStatus.RUNNING, "● Running", "#2563eb"),
        (PreviewRowStatus.SUCCESS, "✓ Success", "#16a34a"),
        (PreviewRowStatus.FAILED, "✕ Failed", "#dc2626"),
        (PreviewRowStatus.SKIPPED, "— Skipped", "#ca8a04"),
        (PreviewRowStatus.INVALID, "! Invalid", "#ea580c"),
        (PreviewRowStatus.RETRIED, "↻ Retried", "#2563eb"),
    )

    for status, label, color_name in expected:
        model.set_row_status(0, status)
        assert model.data(index) == label
        color = model.data(index, Qt.ItemDataRole.ForegroundRole)
        assert isinstance(color, QColor)
        assert color.name() == color_name
        assert (
            model.data(index, Qt.ItemDataRole.TextAlignmentRole)
            == Qt.AlignmentFlag.AlignCenter
        )

    assert model.data(index, Qt.ItemDataRole.EditRole) is None


def test_row_status_validation_and_reset():
    import pytest

    from app.models.preview_row_status import PreviewRowStatus

    model = ExcelTableModel(["A"], [[1], [2]], show_status_column=True)

    with pytest.raises(IndexError, match="out of range"):
        model.row_status(-1)
    with pytest.raises(IndexError, match="out of range"):
        model.set_row_status(2, PreviewRowStatus.SUCCESS)
    with pytest.raises(TypeError, match="PreviewRowStatus"):
        model.set_row_status(0, "success")  # type: ignore[arg-type]

    model.reset_row_statuses()
    model.set_row_status(0, PreviewRowStatus.SUCCESS)
    assert model.row_status(0) is PreviewRowStatus.SUCCESS

    model.set_row_status(0, PreviewRowStatus.PENDING)
    assert model.row_status(0) is PreviewRowStatus.PENDING

    model.set_row_status(1, PreviewRowStatus.FAILED)
    model.reset_row_statuses()
    assert model.row_status(1) is PreviewRowStatus.PENDING


def test_statuses_reset_when_model_data_source_changes():
    from app.models.preview_row_status import PreviewRowStatus

    model = ExcelTableModel(["A"], [[1]], show_status_column=True)
    model.set_row_status(0, PreviewRowStatus.SUCCESS)
    model.set_data(["A"], [[2]])
    assert model.row_status(0) is PreviewRowStatus.PENDING

    source = FakeVirtualSource()
    model.set_row_status(0, PreviewRowStatus.FAILED)
    model.set_source(source)
    assert model.row_status(0) is PreviewRowStatus.PENDING

    model.set_row_status(0, PreviewRowStatus.SUCCESS)
    model.clear_source()
    assert model.columnCount() == 0
