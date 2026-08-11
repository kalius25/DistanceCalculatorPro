import pytest
from PySide6.QtWidgets import QLabel

from app.presentation.pages.about_page import AboutPage
from app.presentation.pages.base_placeholder_page import BasePlaceholderPage
from app.presentation.pages.settings_page import SettingsPage


@pytest.mark.parametrize(
    ("page_type", "expected_title", "expected_description"),
    [
        (
            SettingsPage,
            "Settings",
            (
                "Application settings and provider preferences will be "
                "implemented later."
            ),
        ),
        (
            AboutPage,
            "About",
            "DistanceCalculatorPro application information.",
        ),
    ],
)
def test_placeholder_page_content(
    qtbot,
    page_type: type[BasePlaceholderPage],
    expected_title: str,
    expected_description: str,
) -> None:
    page = page_type()
    qtbot.addWidget(page)

    title = page.findChild(QLabel, "lblPageTitle")
    description = page.findChild(QLabel, "lblPageDescription")

    assert title is not None and title.text() == expected_title
    assert description is not None
    assert description.text() == expected_description
    assert description.wordWrap() is True


def test_base_placeholder_page_accepts_custom_content(qtbot) -> None:
    page = BasePlaceholderPage("Custom", "Custom description")
    qtbot.addWidget(page)

    labels = page.findChildren(QLabel)

    assert [label.text() for label in labels] == [
        "Custom",
        "Custom description",
    ]
