from PySide6.QtCore import QByteArray, QSettings


class SettingsManager:
    """Persists presentation preferences through Qt settings."""

    THEME_KEY = "appearance/theme"
    WINDOW_GEOMETRY_KEY = "window/geometry"
    WINDOW_STATE_KEY = "window/state"
    TOOLBAR_VISIBLE_KEY = "window/toolbar_visible"
    RECENT_FILES_KEY = "files/recent"
    MAX_RECENT_FILES = 10

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
        recent_files = [
            item for item in recent_files if item != normalized_path
        ]
        recent_files.insert(0, normalized_path)
        self._settings.setValue(
            self.RECENT_FILES_KEY,
            recent_files[: self.MAX_RECENT_FILES],
        )

    def clear_recent_files(self) -> None:
        self._settings.remove(self.RECENT_FILES_KEY)
