from PySide6.QtWidgets import QLabel

from app.presentation.pages.base_placeholder_page import BasePlaceholderPage


def test_base_placeholder_page_accepts_custom_content(qtbot) -> None:
    page = BasePlaceholderPage("Custom", "Custom description")
    qtbot.addWidget(page)

    labels = page.findChildren(QLabel)

    assert [label.text() for label in labels] == [
        "Custom",
        "Custom description",
    ]
