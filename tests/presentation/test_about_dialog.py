from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel

from app.presentation.app_metadata import AppMetadata
from app.presentation.dialogs.about_dialog import AboutDialog


def test_about_dialog_initial_state_and_content(qtbot) -> None:
    metadata = AppMetadata(name="DCP Test", version="9.9.9")
    dialog = AboutDialog(metadata)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "About DCP Test"
    assert dialog.isModal() is True
    assert dialog.minimumWidth() == 480
    assert dialog.maximumWidth() == 480

    title = dialog.findChild(QLabel, "lblAboutTitle")
    version = dialog.findChild(QLabel, "lblAboutVersion")
    description = dialog.findChild(QLabel, "lblAboutDescription")
    release = dialog.findChild(QLabel, "lblAboutRelease")

    assert title is not None and title.text() == "DCP Test"
    assert version is not None and version.text() == "Version 9.9.9"
    assert description is not None and description.wordWrap() is True
    assert release is not None
    assert release.text() == "Release channel: v1.3 · Release Candidate 1"
    assert title.alignment() == Qt.AlignmentFlag.AlignCenter


def test_ok_button_accepts_dialog(qtbot) -> None:
    dialog = AboutDialog(AppMetadata())
    qtbot.addWidget(dialog)

    dialog._button_box.accepted.emit()

    assert dialog.result() == AboutDialog.DialogCode.Accepted
