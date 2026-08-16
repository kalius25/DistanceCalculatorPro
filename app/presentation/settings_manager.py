from PySide6.QtCore import QByteArray, QSettings


class SettingsManager:
    """Persists presentation preferences through Qt settings."""

    THEME_KEY = "appearance/theme"
    WINDOW_GEOMETRY_KEY = "window/geometry"
    WINDOW_STATE_KEY = "window/state"
    TOOLBAR_VISIBLE_KEY = "window/toolbar_visible"
    WORKSPACE_PANELS_VISIBLE_KEY = "workspace/file_panels_visible"
    WORKSPACE_SPLITTER_STATE_KEY = "workspace/splitter_state"
    RECENT_FILES_KEY = "files/recent"
    MAX_RECENT_FILES = 10
    DEBUG_ENABLED_KEY = "debug/enabled"
    TRACE_BROWSER_KEY = "debug/trace_browser"
    PARSER_DIAGNOSTICS_KEY = "debug/parser_diagnostics"
    SAVE_HTML_KEY = "debug/save_html"
    SAVE_SCREENSHOT_KEY = "debug/save_screenshot"
    SAVE_JSON_KEY = "debug/save_json"

    def __init__(self, settings: QSettings) -> None:
        self._settings = settings

    def theme_name(self, default: str = "light") -> str:
        value = self._settings.value(self.THEME_KEY, defaultValue=default)
        return str(value)

    def set_theme_name(self, theme_name: str) -> None:
        self._settings.setValue(self.THEME_KEY, theme_name)

    def window_geometry(self) -> QByteArray | None:
        value = self._settings.value(self.WINDOW_GEOMETRY_KEY)
        return value if isinstance(value, QByteArray) else None

    def set_window_geometry(self, geometry: QByteArray) -> None:
        self._settings.setValue(self.WINDOW_GEOMETRY_KEY, geometry)

    def window_state(self) -> QByteArray | None:
        value = self._settings.value(self.WINDOW_STATE_KEY)
        return value if isinstance(value, QByteArray) else None

    def set_window_state(self, state: QByteArray) -> None:
        self._settings.setValue(self.WINDOW_STATE_KEY, state)

    def toolbar_visible(self, default: bool = True) -> bool:
        value = self._settings.value(
            self.TOOLBAR_VISIBLE_KEY,
            defaultValue=default,
            type=bool,
        )
        return bool(value)

    def set_toolbar_visible(self, visible: bool) -> None:
        self._settings.setValue(self.TOOLBAR_VISIBLE_KEY, visible)

    def workspace_panels_visible(self, default: bool = True) -> bool:
        return self._bool_value(self.WORKSPACE_PANELS_VISIBLE_KEY, default)

    def set_workspace_panels_visible(self, visible: bool) -> None:
        self._settings.setValue(self.WORKSPACE_PANELS_VISIBLE_KEY, visible)

    def workspace_splitter_state(self) -> QByteArray | None:
        value = self._settings.value(self.WORKSPACE_SPLITTER_STATE_KEY)
        return value if isinstance(value, QByteArray) else None

    def set_workspace_splitter_state(self, state: QByteArray) -> None:
        self._settings.setValue(self.WORKSPACE_SPLITTER_STATE_KEY, state)

    def recent_files(self) -> list[str]:
        value = self._settings.value(self.RECENT_FILES_KEY, defaultValue=[])
        if isinstance(value, str):
            return [value]
        if isinstance(value, list):
            return [str(item) for item in value]
        return []

    def add_recent_file(self, file_path: str) -> None:
        normalized_path = file_path.strip()
        if not normalized_path:
            return
        recent_files = self.recent_files()
        recent_files = [item for item in recent_files if item != normalized_path]
        recent_files.insert(0, normalized_path)
        self._settings.setValue(
            self.RECENT_FILES_KEY,
            recent_files[: self.MAX_RECENT_FILES],
        )

    def remove_recent_file(self, file_path: str) -> None:
        normalized_path = file_path.strip()
        if not normalized_path:
            return
        recent_files = [
            item for item in self.recent_files() if item != normalized_path
        ]
        if recent_files:
            self._settings.setValue(self.RECENT_FILES_KEY, recent_files)
        else:
            self._settings.remove(self.RECENT_FILES_KEY)

    def clear_recent_files(self) -> None:
        self._settings.remove(self.RECENT_FILES_KEY)

    def debug_enabled(self, default: bool = False) -> bool:
        return self._bool_value(self.DEBUG_ENABLED_KEY, default)

    def set_debug_enabled(self, enabled: bool) -> None:
        self._settings.setValue(self.DEBUG_ENABLED_KEY, enabled)

    def trace_browser(self, default: bool = False) -> bool:
        return self._bool_value(self.TRACE_BROWSER_KEY, default)

    def set_trace_browser(self, enabled: bool) -> None:
        self._settings.setValue(self.TRACE_BROWSER_KEY, enabled)

    def parser_diagnostics(self, default: bool = False) -> bool:
        return self._bool_value(self.PARSER_DIAGNOSTICS_KEY, default)

    def set_parser_diagnostics(self, enabled: bool) -> None:
        self._settings.setValue(self.PARSER_DIAGNOSTICS_KEY, enabled)

    def save_html(self, default: bool = False) -> bool:
        return self._bool_value(self.SAVE_HTML_KEY, default)

    def set_save_html(self, enabled: bool) -> None:
        self._settings.setValue(self.SAVE_HTML_KEY, enabled)

    def save_screenshot(self, default: bool = False) -> bool:
        return self._bool_value(self.SAVE_SCREENSHOT_KEY, default)

    def set_save_screenshot(self, enabled: bool) -> None:
        self._settings.setValue(self.SAVE_SCREENSHOT_KEY, enabled)

    def save_json(self, default: bool = False) -> bool:
        return self._bool_value(self.SAVE_JSON_KEY, default)

    def set_save_json(self, enabled: bool) -> None:
        self._settings.setValue(self.SAVE_JSON_KEY, enabled)

    def _bool_value(self, key: str, default: bool) -> bool:
        value = self._settings.value(key, defaultValue=default, type=bool)
        return bool(value)
