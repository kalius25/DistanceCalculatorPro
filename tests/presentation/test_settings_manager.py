from pathlib import Path

import pytest
from PySide6.QtCore import QByteArray, QSettings

from app.presentation.settings_manager import SettingsManager


@pytest.fixture
def qt_settings(tmp_path: Path) -> QSettings:
    settings = QSettings(
        str(tmp_path / "settings.ini"),
        QSettings.Format.IniFormat,
    )
    settings.clear()
    return settings


@pytest.fixture
def manager(qt_settings: QSettings) -> SettingsManager:
    return SettingsManager(qt_settings)


def test_theme_name_uses_default_and_persists_value(
    manager: SettingsManager,
) -> None:
    assert manager.theme_name() == "light"
    assert manager.theme_name("dark") == "dark"

    manager.set_theme_name("dark")

    assert manager.theme_name() == "dark"


def test_window_geometry_returns_only_qbytearray(
    manager: SettingsManager,
    qt_settings: QSettings,
) -> None:
    assert manager.window_geometry() is None

    geometry = QByteArray(b"geometry")
    manager.set_window_geometry(geometry)
    assert manager.window_geometry() == geometry

    qt_settings.setValue(SettingsManager.WINDOW_GEOMETRY_KEY, "invalid")
    assert manager.window_geometry() is None


def test_window_state_returns_only_qbytearray(
    manager: SettingsManager,
    qt_settings: QSettings,
) -> None:
    assert manager.window_state() is None

    state = QByteArray(b"state")
    manager.set_window_state(state)
    assert manager.window_state() == state

    qt_settings.setValue(SettingsManager.WINDOW_STATE_KEY, 123)
    assert manager.window_state() is None


def test_toolbar_visibility_uses_default_and_persists_value(
    manager: SettingsManager,
) -> None:
    assert manager.toolbar_visible() is True
    assert manager.toolbar_visible(default=False) is False

    manager.set_toolbar_visible(False)

    assert manager.toolbar_visible() is False


def test_recent_files_supports_string_list_and_invalid_value(
    manager: SettingsManager,
    qt_settings: QSettings,
) -> None:
    assert manager.recent_files() == []

    qt_settings.setValue(SettingsManager.RECENT_FILES_KEY, "one.xlsx")
    assert manager.recent_files() == ["one.xlsx"]

    qt_settings.setValue(SettingsManager.RECENT_FILES_KEY, ["one.xlsx", 2])
    assert manager.recent_files() == ["one.xlsx", "2"]

    qt_settings.setValue(SettingsManager.RECENT_FILES_KEY, 42)
    assert manager.recent_files() == []


def test_add_recent_file_ignores_blank_value(manager: SettingsManager) -> None:
    manager.add_recent_file("   ")

    assert manager.recent_files() == []


def test_add_recent_file_normalizes_deduplicates_and_moves_to_front(
    manager: SettingsManager,
) -> None:
    manager.add_recent_file(" first.xlsx ")
    manager.add_recent_file("second.xlsx")
    manager.add_recent_file("first.xlsx")

    assert manager.recent_files() == ["first.xlsx", "second.xlsx"]


def test_add_recent_file_limits_history(manager: SettingsManager) -> None:
    for index in range(SettingsManager.MAX_RECENT_FILES + 2):
        manager.add_recent_file(f"file-{index}.xlsx")

    recent_files = manager.recent_files()

    assert len(recent_files) == SettingsManager.MAX_RECENT_FILES
    assert recent_files[0] == "file-11.xlsx"
    assert recent_files[-1] == "file-2.xlsx"


def test_clear_recent_files(manager: SettingsManager) -> None:
    manager.add_recent_file("one.xlsx")

    manager.clear_recent_files()

    assert manager.recent_files() == []


def test_debug_preferences_use_defaults_and_persist(
    manager: SettingsManager,
) -> None:
    assert manager.debug_enabled() is False
    assert manager.trace_browser() is False
    assert manager.parser_diagnostics() is False
    assert manager.save_html() is False
    assert manager.save_screenshot() is False
    assert manager.save_json() is False

    manager.set_debug_enabled(True)
    manager.set_trace_browser(True)
    manager.set_parser_diagnostics(True)
    manager.set_save_html(True)
    manager.set_save_screenshot(True)
    manager.set_save_json(True)

    assert manager.debug_enabled() is True
    assert manager.trace_browser() is True
    assert manager.parser_diagnostics() is True
    assert manager.save_html() is True
    assert manager.save_screenshot() is True
    assert manager.save_json() is True


def test_workspace_panel_visibility_uses_default_and_persists_value(
    manager: SettingsManager,
) -> None:
    assert manager.workspace_panels_visible() is True
    assert manager.workspace_panels_visible(default=False) is False

    manager.set_workspace_panels_visible(False)

    assert manager.workspace_panels_visible() is False


def test_workspace_splitter_state_returns_only_qbytearray(
    manager: SettingsManager,
    qt_settings: QSettings,
) -> None:
    assert manager.workspace_splitter_state() is None

    state = QByteArray(b"splitter")
    manager.set_workspace_splitter_state(state)
    assert manager.workspace_splitter_state() == state

    qt_settings.setValue(SettingsManager.WORKSPACE_SPLITTER_STATE_KEY, "invalid")
    assert manager.workspace_splitter_state() is None
