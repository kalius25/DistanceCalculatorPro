from pathlib import Path
from unittest.mock import MagicMock

from app.presentation.pages.history_page import HistoryPage


def test_history_page_empty_state(qtbot: object) -> None:
    page = HistoryPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    assert page.recent_files == []
    assert page._recent_files.count() == 1
    assert page._recent_files.item(0).text() == "No recent workbooks"
    assert not page._open_button.isEnabled()
    assert not page._remove_button.isEnabled()
    assert not page._clear_button.isEnabled()


def test_history_page_populates_and_selects_recent_file(
    qtbot: object,
    tmp_path: Path,
) -> None:
    first = str(tmp_path / "A.xlsx")
    second = str(tmp_path / "B.csv")
    page = HistoryPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page.set_recent_files([first, second])
    page._recent_files.setCurrentRow(0)

    assert page.recent_files == [first, second]
    assert page._recent_files.item(0).text() == "A.xlsx"
    assert page._recent_files.item(0).toolTip() == first
    assert page._open_button.isEnabled()
    assert page._remove_button.isEnabled()
    assert page._clear_button.isEnabled()


def test_history_page_emits_open_remove_and_clear(
    qtbot: object,
    tmp_path: Path,
) -> None:
    file_path = str(tmp_path / "A.xlsx")
    page = HistoryPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    page.set_recent_files([file_path])
    page._recent_files.setCurrentRow(0)

    open_spy = MagicMock()
    remove_spy = MagicMock()
    clear_spy = MagicMock()
    page.open_requested.connect(open_spy)
    page.remove_requested.connect(remove_spy)
    page.clear_requested.connect(clear_spy)

    page._open_button.click()
    page._remove_button.click()
    page._clear_button.click()
    page._open_item(page._recent_files.item(0))

    assert open_spy.call_count == 2
    open_spy.assert_called_with(file_path)
    remove_spy.assert_called_once_with(file_path)
    clear_spy.assert_called_once_with()


def test_history_page_no_selection_actions_are_safe(qtbot: object) -> None:
    page = HistoryPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page._open_selected()
    page._remove_selected()
    page._open_item(page._recent_files.item(0))

    assert not page._open_button.isEnabled()
    assert not page._remove_button.isEnabled()
