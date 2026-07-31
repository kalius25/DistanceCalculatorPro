from PySide6.QtCore import Qt

from app.presentation.widgets.navigation_panel import NavigationPanel


def test_navigation_items_and_initial_selection(qtbot) -> None:
    panel = NavigationPanel()
    qtbot.addWidget(panel)

    assert panel.objectName() == "lstNavigation"
    assert panel.width() == 190
    assert panel.count() == 4
    assert panel.currentRow() == 0

    expected = (
        ("Home", "home"),
        ("History", "history"),
        ("Settings", "settings"),
        ("About", "about"),
    )
    actual = tuple(
        (panel.item(index).text(), panel.item(index).data(Qt.ItemDataRole.UserRole))
        for index in range(panel.count())
    )
    assert actual == expected


def test_current_row_change_emits_page_changed(qtbot) -> None:
    panel = NavigationPanel()
    qtbot.addWidget(panel)

    with qtbot.waitSignal(panel.page_changed, timeout=1000) as blocker:
        panel.setCurrentRow(2)

    assert blocker.args == [2]
