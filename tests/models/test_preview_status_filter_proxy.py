from PySide6.QtGui import QStandardItemModel

from app.models.excel_table_model import ExcelTableModel
from app.models.preview_row_status import PreviewRowStatus
from app.models.preview_status_filter_proxy import PreviewStatusFilterProxyModel


def _status_model() -> ExcelTableModel:
    model = ExcelTableModel(
        ["Origin"],
        [["A"], ["B"], ["C"]],
        show_status_column=True,
    )
    model.set_row_status(1, PreviewRowStatus.FAILED)
    model.set_row_status(2, PreviewRowStatus.INVALID)
    return model


def test_status_filter_defaults_to_all_rows_and_filters_statuses() -> None:
    source = _status_model()
    proxy = PreviewStatusFilterProxyModel()
    proxy.setSourceModel(source)

    assert proxy.statuses is None
    assert proxy.rowCount() == 3

    proxy.set_statuses({PreviewRowStatus.FAILED})

    assert proxy.statuses == frozenset({PreviewRowStatus.FAILED})
    assert proxy.rowCount() == 1
    assert proxy.data(proxy.index(0, 1)) == "B"

    proxy.set_statuses({PreviewRowStatus.FAILED})
    assert proxy.rowCount() == 1

    proxy.set_statuses(None)
    assert proxy.rowCount() == 3


def test_status_filter_allows_non_excel_source_model() -> None:
    source = QStandardItemModel(2, 1)
    proxy = PreviewStatusFilterProxyModel()
    proxy.setSourceModel(source)
    proxy.set_statuses({PreviewRowStatus.FAILED})

    assert proxy.rowCount() == 2


def test_refresh_filter_re_evaluates_active_filter() -> None:
    source = _status_model()
    proxy = PreviewStatusFilterProxyModel()
    proxy.setSourceModel(source)
    proxy.set_statuses({PreviewRowStatus.FAILED})

    assert proxy.rowCount() == 1
    proxy.refresh_filter()
    assert proxy.rowCount() == 1
