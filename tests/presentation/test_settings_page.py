from unittest.mock import MagicMock

from app.presentation.pages.settings_page import SettingsPage


def test_settings_page_initial_state(qtbot: object) -> None:
    page = SettingsPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    assert page.theme_name == "light"
    assert page.diagnostics_state == (False, False, False, False, False, False)
    assert not page._trace_browser.isEnabled()
    assert not page._parser_diagnostics.isEnabled()
    assert not page._save_html.isEnabled()
    assert not page._save_screenshot.isEnabled()
    assert not page._save_json.isEnabled()


def test_settings_page_set_theme_supports_known_and_unknown_values(
    qtbot: object,
) -> None:
    page = SettingsPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]

    page.set_theme("dark")
    assert page.theme_name == "dark"

    page.set_theme("unsupported")
    assert page.theme_name == "light"


def test_settings_page_theme_change_emits_selected_theme(qtbot: object) -> None:
    page = SettingsPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    spy = MagicMock()
    page.theme_changed.connect(spy)

    page._theme_combo.setCurrentIndex(1)

    spy.assert_called_once_with("dark")


def test_settings_page_set_diagnostics_synchronizes_without_emitting(
    qtbot: object,
) -> None:
    page = SettingsPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    spy = MagicMock()
    page.diagnostics_changed.connect(spy)

    page.set_diagnostics(True, True, False, True, False, True)

    assert page.diagnostics_state == (True, True, False, True, False, True)
    assert page._trace_browser.isEnabled()
    assert page._parser_diagnostics.isEnabled()
    spy.assert_not_called()


def test_settings_page_user_toggle_emits_complete_diagnostics_state(
    qtbot: object,
) -> None:
    page = SettingsPage()
    qtbot.addWidget(page)  # type: ignore[attr-defined]
    spy = MagicMock()
    page.diagnostics_changed.connect(spy)

    page._debug_enabled.setChecked(True)
    page._trace_browser.setChecked(True)

    assert page._trace_browser.isEnabled()
    assert spy.call_args_list[-1].args == (
        True,
        True,
        False,
        False,
        False,
        False,
    )

    page._debug_enabled.setChecked(False)

    assert not page._trace_browser.isEnabled()
    assert spy.call_args_list[-1].args == (
        False,
        True,
        False,
        False,
        False,
        False,
    )
