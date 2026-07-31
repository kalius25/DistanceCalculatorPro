from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QMimeData, QPoint, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import QListWidgetItem

from app.presentation.pages.home_page import HomePage


def test_initial_workspace_state(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    assert page.acceptDrops()
    assert page.selected_file is None
    assert not page._file_information_frame.isVisible()
    assert page._empty_file_information.isVisibleTo(page)
    assert page._workspace_status.text() == "No workbook selected"
    assert page._recent_files.count() == 1
    assert page._recent_files.item(0).text() == "No recent workbooks"
    assert not bool(
        page._recent_files.item(0).flags() & Qt.ItemFlag.ItemIsEnabled
    )


def test_supported_extensions_are_case_insensitive() -> None:
    assert HomePage.accepts_file("book.xlsx")
    assert HomePage.accepts_file("book.XLSM")
    assert HomePage.accepts_file("book.CsV")
    assert not HomePage.accepts_file("book.xls")
    assert not HomePage.accepts_file("book.txt")


def test_set_and_clear_selected_file(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    file_path = str(Path("C:/reports/routes.xlsx"))

    page.set_selected_file(file_path)

    assert page.selected_file == file_path
    assert page._selected_file_name.text() == "routes.xlsx"
    assert page._selected_file_path.text() == file_path
    assert page._selected_file_path.toolTip() == file_path
    assert not page._empty_file_information.isVisible()
    assert page._workspace_status.text() == "Inspecting workbook…"

    page.clear_selected_file()

    assert page.selected_file is None
    assert not page._file_information_frame.isVisible()
    assert page._workspace_status.text() == "No workbook selected"


def test_browse_button_emits_browse_request(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    with qtbot.waitSignal(page.browse_requested):  # type: ignore[attr-defined]
        page._browse_button.click()


def test_clear_recent_button_emits_request(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_recent_files(["C:/data/routes.xlsx"])

    with qtbot.waitSignal(page.clear_recent_requested):  # type: ignore[attr-defined]
        page._clear_recent_button.click()


def test_recent_files_are_rendered_and_activated(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    first = str(Path("C:/data/first.xlsx"))
    second = str(Path("D:/data/second.csv"))

    page.set_recent_files([first, second])

    assert page._recent_files.count() == 2
    assert page._recent_files.item(0).text() == "first.xlsx"
    assert page._recent_files.item(0).toolTip() == first
    assert page._recent_files.item(1).text() == "second.csv"

    with qtbot.waitSignal(  # type: ignore[attr-defined]
        page.file_selected,
        check_params_cb=lambda value: value == second,
    ):
        page._recent_files.itemActivated.emit(page._recent_files.item(1))


def test_recent_item_without_string_path_is_ignored(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    item = QListWidgetItem("invalid")

    with qtbot.assertNotEmitted(page.file_selected):  # type: ignore[attr-defined]
        page._on_recent_file_activated(item)


def _mime_data(file_path: str) -> QMimeData:
    mime_data = QMimeData()
    mime_data.setUrls([QUrl.fromLocalFile(file_path)])
    return mime_data


def test_drag_enter_accepts_supported_local_file(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    mime_data = _mime_data("C:/data/routes.xlsx")
    event = QDragEnterEvent(
        QPoint(10, 10),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    page.dragEnterEvent(event)

    assert event.isAccepted()
    assert page._drop_zone.property("dragActive") is True


def test_drag_enter_rejects_unsupported_file(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    mime_data = _mime_data("C:/data/routes.txt")
    event = QDragEnterEvent(
        QPoint(10, 10),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    page.dragEnterEvent(event)

    assert not event.isAccepted()


def test_drop_emits_supported_file_and_resets_state(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    file_path = "C:/data/routes.xlsm"
    page._drop_zone.setProperty("dragActive", True)
    mime_data = _mime_data(file_path)
    event = QDropEvent(
        QPoint(10, 10),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    with qtbot.waitSignal(  # type: ignore[attr-defined]
        page.file_selected,
        check_params_cb=lambda value: value == file_path,
    ):
        page.dropEvent(event)

    assert event.isAccepted()
    assert page._drop_zone.property("dragActive") is False


def test_drop_rejects_multiple_or_unsupported_urls(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    mime_data = QMimeData()
    mime_data.setUrls(
        [
            QUrl.fromLocalFile("C:/data/first.xlsx"),
            QUrl.fromLocalFile("C:/data/second.xlsx"),
        ]
    )
    event = QDropEvent(
        QPoint(10, 10),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    with qtbot.assertNotEmitted(page.file_selected):  # type: ignore[attr-defined]
        page.dropEvent(event)

    assert not event.isAccepted()


def test_non_local_url_is_rejected(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    mime_data = QMimeData()
    mime_data.setUrls([QUrl("https://example.com/routes.xlsx")])
    event = QDragEnterEvent(
        QPoint(10, 10),
        Qt.DropAction.CopyAction,
        mime_data,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier,
    )

    page.dragEnterEvent(event)

    assert not event.isAccepted()


def test_reset_drop_zone_clears_drag_state(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page._drop_zone.setProperty("dragActive", True)

    page._reset_drop_zone()

    assert page._drop_zone.property("dragActive") is False


def test_workbook_inspection_is_rendered_and_sheet_can_change(qtbot: object) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    info = WorkbookInfo(
        file_path="routes.xlsx",
        file_name="routes.xlsx",
        file_type="XLSX",
        file_size_bytes=2048,
        modified_at=datetime(2026, 7, 31, 10, 30),
        worksheets=(
            WorksheetInfo(
                "Routes",
                1200,
                4,
                ("Origin", "Destination"),
                (("A", "B", "8.6"), ("C", "D", "7.1")),
            ),
            WorksheetInfo("Settings", 5, 2, ("Key", "Value")),
        ),
    )

    page.set_inspection(info)

    assert page.workbook_info == info
    assert page._sheet_selector.count() == 2
    assert page._file_size_value.text() == "2.0 KB"
    assert page._row_count_value.text() == "1,200"
    assert page._preview_model.rowCount() == 2
    assert page._preview_model.columnCount() == 4
    assert page._preview_model.item(0, 0).text() == "A"

    with qtbot.waitSignal(page.sheet_changed):  # type: ignore[attr-defined]
        page._sheet_selector.setCurrentIndex(1)
    assert page._row_count_value.text() == "5"


def test_inspection_error_clears_metadata(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page.set_inspection_error("Invalid workbook")

    assert page.workbook_info is None
    assert not page._inspector_frame.isVisible()
    assert page._workspace_status.text() == "Inspection failed · Invalid workbook"


def test_preview_row_selector_supports_configured_limits(qtbot: object) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    preview_rows = tuple(
        (str(index), f"Value {index}") for index in range(1, 501)
    )
    info = WorkbookInfo(
        file_path="preview.xlsx",
        file_name="preview.xlsx",
        file_type="XLSX",
        file_size_bytes=1024,
        modified_at=datetime(2026, 7, 31, 14, 0),
        worksheets=(
            WorksheetInfo(
                "Data",
                501,
                2,
                ("Index", "Value"),
                preview_rows,
            ),
        ),
    )

    page.set_inspection(info)

    assert page._preview_rows_selector.count() == 5
    assert [
        page._preview_rows_selector.itemText(index)
        for index in range(page._preview_rows_selector.count())
    ] == ["20", "50", "100", "200", "500"]
    assert page._preview_model.rowCount() == 20
    assert page._preview_title.text() == "Data Preview (first 20 rows)"

    for limit in (50, 100, 200, 500):
        page._preview_rows_selector.setCurrentText(str(limit))
        assert page._preview_model.rowCount() == limit
        assert page._preview_title.text() == f"Data Preview (first {limit} rows)"

    assert page._preview_model.item(0, 1).toolTip() == "Value 1"


def test_source_panels_can_be_hidden_and_shown(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.show()

    assert page._source_panels_container.isVisible()
    assert page._toggle_source_panels_button.text() == "Hide file panels"

    page._toggle_source_panels_button.click()

    assert not page._source_panels_container.isVisible()
    assert page._toggle_source_panels_button.text() == "Show file panels"

    page._toggle_source_panels_button.click()

    assert page._source_panels_container.isVisible()
    assert page._toggle_source_panels_button.text() == "Hide file panels"


def test_workspace_guidance_stays_visible_when_source_panels_are_toggled(
    qtbot: object,
) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.resize(1200, 800)
    page.show()

    description_parent = page._description_label.parentWidget()
    status_parent = page._workspace_status.parentWidget()

    page._toggle_source_panels_button.click()

    assert description_parent is page._workspace_header
    assert status_parent is page._workspace_header
    assert page._description_label.isVisible()
    assert page._workspace_status.isVisible()
    assert page._workspace_status.text() == "No workbook selected"

    page._toggle_source_panels_button.click()

    assert page._description_label.isVisible()
    assert page._workspace_status.isVisible()

def test_invalid_preview_row_limit_is_ignored(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page._on_preview_row_limit_changed("invalid")
    page._on_preview_row_limit_changed("7")

    assert page._preview_row_limit == 20
