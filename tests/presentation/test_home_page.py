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
    assert not page._selected_file_frame.isVisible()
    assert page._empty_state_label.isVisibleTo(page)
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
    assert not page._empty_state_label.isVisible()
    assert page._workspace_status.text() == (
        "Workbook selected · Ready to inspect"
    )

    page.clear_selected_file()

    assert page.selected_file is None
    assert not page._selected_file_frame.isVisible()
    assert page._workspace_status.text() == "No workbook selected"


def test_browse_and_change_buttons_emit_browse_request(qtbot: object) -> None:
    with patch("app.presentation.pages.home_page.qta.icon", return_value=QIcon()):
        page = HomePage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    with qtbot.waitSignal(page.browse_requested):  # type: ignore[attr-defined]
        page._browse_button.click()
    with qtbot.waitSignal(page.browse_requested):  # type: ignore[attr-defined]
        page._change_button.click()


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
    event = QDragEnterEvent(
        QPoint(10, 10),
        Qt.DropAction.CopyAction,
        _mime_data("C:/data/routes.xlsx"),
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
    event = QDragEnterEvent(
        QPoint(10, 10),
        Qt.DropAction.CopyAction,
        _mime_data("C:/data/routes.txt"),
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
    event = QDropEvent(
        QPoint(10, 10),
        Qt.DropAction.CopyAction,
        _mime_data(file_path),
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
