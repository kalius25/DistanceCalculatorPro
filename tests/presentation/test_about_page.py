from unittest.mock import MagicMock

from PySide6.QtWidgets import QLabel

from app.presentation.app_metadata import AppMetadata
from app.presentation.pages.about_page import AboutPage


def test_about_page_uses_application_metadata(qtbot) -> None:
    metadata = AppMetadata(
        name="DCP Test",
        version="9.9.9",
        organization="Test Org",
    )
    page = AboutPage(metadata)
    qtbot.addWidget(page)

    assert page.findChild(QLabel, "lblPageTitle").text() == "About"
    assert page.findChild(QLabel, "lblAboutPageProduct").text() == "DCP Test"
    assert page.findChild(QLabel, "lblAboutPageVersion").text() == "Version 9.9.9"
    assert (
        page.findChild(QLabel, "lblAboutPageOrganization").text()
        == "Organization: Test Org"
    )
    assert (
        "Release Candidate"
        in page.findChild(
            QLabel,
            "lblAboutPageRelease",
        ).text()
    )


def test_about_page_defaults_to_application_metadata(qtbot) -> None:
    page = AboutPage()
    qtbot.addWidget(page)

    assert (
        page.findChild(
            QLabel,
            "lblAboutPageProduct",
        ).text()
        == "DistanceCalculatorPro"
    )


def test_about_page_details_button_emits_signal(qtbot) -> None:
    page = AboutPage()
    qtbot.addWidget(page)
    spy = MagicMock()
    page.details_requested.connect(spy)

    page._details_button.click()

    spy.assert_called_once_with()
