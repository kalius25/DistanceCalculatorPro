from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from PySide6.QtCore import QMimeData, QPoint, Qt, QUrl
from PySide6.QtGui import QDragEnterEvent, QDropEvent, QIcon
from PySide6.QtWidgets import QListWidgetItem

from app.presentation.pages.home_page import HomePage
from app.workbooks.models import WorkbookInfo, WorksheetInfo


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

    assert page.selected_sheet_name is None
    page.set_inspection(info)

    assert page.workbook_info == info
    assert page.selected_sheet_name == "Routes"
    assert page._sheet_selector.count() == 2
    assert page._file_size_value.text() == "2.0 KB (2,048 bytes)"
    assert page._row_count_value.text() == "1,200"
    assert page._preview_model.rowCount() == 2
    assert page._preview_model.columnCount() == 4
    assert page._preview_model.item(0, 0).text() == "A"

    with qtbot.waitSignal(page.sheet_changed):  # type: ignore[attr-defined]
        page._sheet_selector.setCurrentIndex(1)
    assert page._row_count_value.text() == "5"


def test_successful_inspection_automatically_hides_file_panels(
    qtbot: object,
) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.show()
    info = WorkbookInfo(
        file_path="routes.xlsx",
        file_name="routes.xlsx",
        file_type="XLSX",
        file_size_bytes=2048,
        modified_at=datetime(2026, 7, 31, 10, 30),
        worksheets=(
            WorksheetInfo(
                "Routes",
                2,
                3,
                ("Origin", "Destination", "Distance"),
                (("A", "B", "8.6"),),
            ),
        ),
    )

    page.set_inspection(info)

    assert page._toggle_source_panels_button.isChecked()
    assert not page._source_panels_container.isVisible()
    assert page._toggle_source_panels_button.text() == "Show file panels"

    page._toggle_source_panels_button.click()

    assert page._source_panels_container.isVisible()
    assert page._toggle_source_panels_button.text() == "Hide file panels"


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


def test_column_mapping_auto_detects_common_headers(qtbot: object) -> None:
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
                10,
                3,
                ("TỌA ĐỘ NƠI ĐI", "TỌA ĐỘ NƠI ĐẾN", "KẾT QUẢ"),
            ),
        ),
    )

    with qtbot.waitSignal(page.column_mapping_changed):  # type: ignore[attr-defined]
        page.set_inspection(info)

    assert page._origin_column_selector.currentText() == "TỌA ĐỘ NƠI ĐI"
    assert page._destination_column_selector.currentText() == "TỌA ĐỘ NƠI ĐẾN"
    assert page._result_column_selector.currentText() == "KẾT QUẢ"
    assert page._mapping_valid
    assert page._mapping_status.text() == "Mapping ready"


def test_column_mapping_rejects_duplicate_roles(qtbot: object) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_inspection(
        WorkbookInfo(
            file_path="routes.csv",
            file_name="routes.csv",
            file_type="CSV",
            file_size_bytes=100,
            modified_at=datetime(2026, 7, 31),
            worksheets=(
                WorksheetInfo("routes", 2, 3, ("From", "To", "Distance")),
            ),
        )
    )

    page._destination_column_selector.setCurrentText("From")

    assert not page._mapping_valid
    assert page._mapping_status.text() == "Each role must use a different column"


def test_column_mapping_resets_when_inspection_is_cleared(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page.clear_inspection()

    assert page._origin_column_selector.count() == 1
    assert page._destination_column_selector.count() == 1
    assert page._result_column_selector.count() == 1
    assert not page._mapping_valid


def test_workbook_without_worksheets_shows_empty_inspector_state(qtbot: object) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    info = WorkbookInfo(
        file_path="empty.xlsx",
        file_name="empty.xlsx",
        file_type="XLSX",
        file_size_bytes=0,
        modified_at=datetime(2026, 7, 31, 15, 0),
        worksheets=(),
    )

    page.set_inspection(info)

    assert page._workspace_status.text() == "Workbook contains no worksheets"
    assert page._row_count_value.text() == "0"
    assert page._column_count_value.text() == "0"
    assert page._headers_status_value.text() == "No"


def test_drag_leave_resets_drop_zone(qtbot: object) -> None:
    from PySide6.QtGui import QDragLeaveEvent

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page._drop_zone.setProperty("dragActive", True)

    page.dragLeaveEvent(QDragLeaveEvent())

    assert page._drop_zone.property("dragActive") is False


def test_preview_extends_missing_headers_and_handles_no_rows(qtbot: object) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    info = WorkbookInfo(
        file_path="wide.xlsx",
        file_name="wide.xlsx",
        file_type="XLSX",
        file_size_bytes=1,
        modified_at=datetime(2026, 7, 31, 15, 0),
        worksheets=(
            WorksheetInfo("Wide", 1, 3, ("Only header",), ()),
        ),
    )

    page.set_inspection(info)

    assert page._preview_model.columnCount() == 3
    assert page._preview_model.headerData(1, Qt.Orientation.Horizontal) == "Column 2"
    assert page._preview_title.text() == "Data Preview (no data rows)"


def test_preview_limit_change_without_current_worksheet_is_safe(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page._on_preview_row_limit_changed("50")

    assert page._preview_row_limit == 50


def test_unknown_sheet_name_is_ignored(qtbot: object) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_inspection(
        WorkbookInfo(
            file_path="routes.xlsx",
            file_name="routes.xlsx",
            file_type="XLSX",
            file_size_bytes=1,
            modified_at=datetime(2026, 7, 31, 15, 0),
            worksheets=(WorksheetInfo("Routes", 1, 1, ("A",)),),
        )
    )

    with qtbot.assertNotEmitted(page.sheet_changed):  # type: ignore[attr-defined]
        page._on_sheet_changed("Missing")


def test_file_size_formatter_covers_bytes_kilobytes_and_megabytes() -> None:
    assert HomePage._format_file_size(100) == "100 B"
    assert HomePage._format_file_size(2048) == "2.0 KB"
    assert HomePage._format_file_size(2 * 1024 * 1024) == "2.0 MB"


def test_column_mapping_without_matching_keywords_remains_unselected(
    qtbot: object,
) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_inspection(
        WorkbookInfo(
            file_path="generic.xlsx",
            file_name="generic.xlsx",
            file_type="XLSX",
            file_size_bytes=1,
            modified_at=datetime(2026, 7, 31, 15, 0),
            worksheets=(WorksheetInfo("Data", 2, 3, ("A", "B", "C")),),
        )
    )

    assert page._origin_column_selector.currentData() == ""
    assert page._destination_column_selector.currentData() == ""
    assert page._result_column_selector.currentData() == ""
    assert page._mapping_status.text() == (
        "Select origin, destination and result columns"
    )


def test_clear_inspection_is_safe_before_widgets_are_created() -> None:
    from types import SimpleNamespace

    incomplete_page = SimpleNamespace()

    HomePage.clear_inspection(incomplete_page)  # type: ignore[arg-type]

    assert incomplete_page._workbook_info is None
    assert incomplete_page._current_worksheet is None


def test_preview_generates_headers_when_worksheet_has_none(qtbot: object) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_inspection(
        WorkbookInfo(
            file_path="headerless.csv",
            file_name="headerless.csv",
            file_type="CSV",
            file_size_bytes=10,
            modified_at=datetime(2026, 7, 31, 15, 30),
            worksheets=(
                WorksheetInfo(
                    "headerless",
                    2,
                    2,
                    (),
                    (("A", "B"),),
                ),
            ),
        )
    )

    assert page._preview_model.columnCount() == 2
    assert (
        page._preview_model.headerData(0, Qt.Orientation.Horizontal)
        == "Column 1"
    )
    assert (
        page._preview_model.headerData(1, Qt.Orientation.Horizontal)
        == "Column 2"
    )


def test_sheet_change_before_inspection_is_ignored(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    with qtbot.assertNotEmitted(page.sheet_changed):  # type: ignore[attr-defined]
        page._on_sheet_changed("Routes")

    assert page.workbook_info is None


def test_provider_configuration_defaults_are_ready(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    assert page._provider_selector.currentText() == "Google Maps Web"
    assert page._travel_mode_selector.currentText() == "Driving"
    assert page._provider_valid
    assert page._provider_status.text() == "Provider ready"
    assert not page._avoid_tolls_checkbox.isChecked()
    assert not page._avoid_highways_checkbox.isChecked()
    assert not page._avoid_ferries_checkbox.isChecked()


def test_provider_configuration_emits_selected_options(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    with qtbot.waitSignal(
        page.provider_configuration_changed,
        check_params_cb=lambda provider, mode, tolls, highways, ferries: (
            provider == "Google Maps Web"
            and mode == "walking"
            and not tolls
            and not highways
            and ferries
        ),
    ):
        page._travel_mode_selector.setCurrentText("Walking")
        page._avoid_ferries_checkbox.setChecked(True)

    assert not page._avoid_tolls_checkbox.isEnabled()
    assert not page._avoid_highways_checkbox.isEnabled()
    assert page._avoid_ferries_checkbox.isEnabled()


def test_provider_configuration_requires_provider_and_mode(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page._provider_selector.setCurrentIndex(-1)

    assert not page._provider_valid
    assert page._provider_status.text() == "Select a provider and travel mode"
    assert page._provider_status.property("valid") is False


def test_workspace_configuration_is_not_ready_without_mapping(
    qtbot: object,
) -> None:
    from app.enums.provider_type import ProviderType
    from app.enums.travel_mode import TravelMode

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    assert page.column_mapping is None
    assert page.provider_configuration is not None
    assert page.provider_configuration.provider is ProviderType.GOOGLE_MAPS_WEB
    assert page.provider_configuration.travel_mode is TravelMode.DRIVING
    assert page.workspace_configuration is None
    assert not page.workspace_ready
    assert page._workspace_readiness_status.text() == "Complete column mapping"


def test_complete_workspace_configuration_emits_ready_state(
    qtbot: object,
) -> None:
    from datetime import datetime

    from app.enums.provider_type import ProviderType
    from app.enums.travel_mode import TravelMode
    from app.presentation.workspace_configuration import WorkspaceConfiguration
    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    configurations: list[WorkspaceConfiguration] = []
    ready_states: list[bool] = []
    page.workspace_configuration_changed.connect(configurations.append)
    page.workspace_ready_changed.connect(ready_states.append)

    page.set_inspection(
        WorkbookInfo(
            file_path="routes.xlsx",
            file_name="routes.xlsx",
            file_type="XLSX",
            file_size_bytes=100,
            modified_at=datetime(2026, 7, 31, 16, 0),
            worksheets=(
                WorksheetInfo(
                    "Routes",
                    2,
                    3,
                    ("Origin", "Destination", "Distance"),
                ),
            ),
        )
    )

    configuration = page.workspace_configuration
    assert configuration is not None
    assert configuration.column_mapping.origin_column == "Origin"
    assert configuration.column_mapping.destination_column == "Destination"
    assert configuration.column_mapping.result_column == "Distance"
    assert configuration.provider_configuration.provider is (
        ProviderType.GOOGLE_MAPS_WEB
    )
    assert configuration.provider_configuration.travel_mode is TravelMode.DRIVING
    assert page.workspace_ready
    assert ready_states == [True]
    assert configurations[-1] == configuration
    assert page._workspace_readiness_status.text() == (
        "Setup ready for calculation"
    )
    assert page._workspace_readiness_status.property("valid") is True


def test_workspace_ready_transition_is_emitted_only_when_state_changes(
    qtbot: object,
) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_inspection(
        WorkbookInfo(
            file_path="routes.xlsx",
            file_name="routes.xlsx",
            file_type="XLSX",
            file_size_bytes=100,
            modified_at=datetime(2026, 7, 31, 16, 0),
            worksheets=(
                WorksheetInfo(
                    "Routes",
                    2,
                    3,
                    ("Origin", "Destination", "Distance"),
                ),
            ),
        )
    )
    ready_states: list[bool] = []
    page.workspace_ready_changed.connect(ready_states.append)

    page._avoid_tolls_checkbox.setChecked(True)
    page._destination_column_selector.setCurrentText("Origin")

    assert ready_states == [False]
    assert not page.workspace_ready
    assert page.column_mapping is None
    assert page._workspace_readiness_status.text() == "Complete column mapping"


def test_workspace_requires_provider_when_mapping_is_complete(
    qtbot: object,
) -> None:
    from datetime import datetime

    from app.workbooks.models import WorkbookInfo, WorksheetInfo

    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_inspection(
        WorkbookInfo(
            file_path="routes.xlsx",
            file_name="routes.xlsx",
            file_type="XLSX",
            file_size_bytes=100,
            modified_at=datetime(2026, 7, 31, 16, 0),
            worksheets=(
                WorksheetInfo(
                    "Routes",
                    2,
                    3,
                    ("Origin", "Destination", "Distance"),
                ),
            ),
        )
    )

    page._provider_selector.setCurrentIndex(-1)

    assert page.provider_configuration is None
    assert page.workspace_configuration is None
    assert not page.workspace_ready
    assert page._workspace_readiness_status.text() == (
        "Complete provider configuration"
    )


def test_workspace_reports_both_incomplete_sections(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page._provider_selector.setCurrentIndex(-1)

    assert page._workspace_readiness_status.text() == (
        "Complete column mapping and provider configuration"
    )
    assert page._workspace_readiness_status.property("valid") is False




def test_mapping_and_provider_share_configuration_row(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    inspector_layout = page._inspector_frame.layout()
    configuration_layout = inspector_layout.itemAt(2).layout()

    assert configuration_layout is not None
    assert configuration_layout.itemAt(0).widget() is page._mapping_frame
    assert configuration_layout.itemAt(1).widget() is page._provider_frame


def test_configuration_inputs_can_be_locked_and_unlocked(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    assert not page.workspace_locked

    page.set_workspace_locked(True)
    assert page.workspace_locked
    assert not page._source_panels_container.isEnabled()
    assert not page._sheet_selector.isEnabled()
    assert not page._preview_rows_selector.isEnabled()
    assert not page._mapping_frame.isEnabled()
    assert not page._provider_frame.isEnabled()

    page.set_workspace_locked(False)
    assert not page.workspace_locked
    assert page._source_panels_container.isEnabled()
    assert page._sheet_selector.isEnabled()
    assert page._preview_rows_selector.isEnabled()
    assert page._mapping_frame.isEnabled()
    assert page._provider_frame.isEnabled()


def test_skip_existing_results_option_updates_workspace_configuration(
    qtbot: object,
) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_inspection(
        WorkbookInfo(
            file_path="routes.xlsx",
            file_name="routes.xlsx",
            file_type="XLSX",
            file_size_bytes=100,
            modified_at=datetime(2026, 8, 2, 20, 0),
            worksheets=(
                WorksheetInfo(
                    "Routes",
                    2,
                    3,
                    ("Origin", "Destination", "Distance"),
                ),
            ),
        )
    )

    assert page.workspace_configuration is not None
    assert page.workspace_configuration.skip_existing_results

    page._skip_existing_results_checkbox.setChecked(False)

    assert page.workspace_configuration is not None
    assert not page.workspace_configuration.skip_existing_results
