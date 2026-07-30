from PySide6.QtCore import QSettings


class SettingsManager:
    """Persists presentation preferences through Qt settings."""

    THEME_KEY = "appearance/theme"
    WINDOW_GEOMETRY_KEY = "window/geometry"
    WINDOW_STATE_KEY = "window/state"

    def __init__(self, settings: QSettings) -> None:
        self._settings = settings

    def theme_name(self, default: str = "light") -> str:
        value = self._settings.value(self.THEME_KEY, defaultValue=default)
        return str(value)

    def set_theme_name(self, theme_name: str) -> None:
        self._settings.setValue(self.THEME_KEY, theme_name)

    def window_geometry(self) -> bytes | None:
        value = self._settings.value(self.WINDOW_GEOMETRY_KEY)
        return bytes(value) if value is not None else None

    def set_window_geometry(self, geometry: bytes) -> None:
        self._settings.setValue(self.WINDOW_GEOMETRY_KEY, geometry)

    def window_state(self) -> bytes | None:
        value = self._settings.value(self.WINDOW_STATE_KEY)
        return bytes(value) if value is not None else None

    def set_window_state(self, state: bytes) -> None:
        self._settings.setValue(self.WINDOW_STATE_KEY, state)
