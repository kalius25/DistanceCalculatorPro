from pathlib import Path

from PySide6.QtWidgets import QApplication


class ThemeManager:
    """Loads and applies application-wide Qt style sheets."""

    SUPPORTED_THEMES = ("light", "dark")

    def __init__(self, styles_directory: Path) -> None:
        self._styles_directory = styles_directory
        self._current_theme = "light"

    @property
    def current_theme(self) -> str:
        return self._current_theme

    def apply_theme(self, application: QApplication, theme_name: str) -> None:
        normalized_theme = theme_name.strip().lower()
        if normalized_theme not in self.SUPPORTED_THEMES:
            supported = ", ".join(self.SUPPORTED_THEMES)
            raise ValueError(
                f"Unsupported theme '{theme_name}'. Supported themes: {supported}."
            )

        theme_path = self._styles_directory / f"{normalized_theme}.qss"
        if not theme_path.is_file():
            raise FileNotFoundError(f"Theme file not found: {theme_path}")

        application.setStyleSheet(theme_path.read_text(encoding="utf-8"))
        self._current_theme = normalized_theme
