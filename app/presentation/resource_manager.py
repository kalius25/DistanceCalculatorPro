import sys
from pathlib import Path


class ResourceManager:
    """Resolves presentation resources from one centralized location."""

    def __init__(self, package_directory: Path) -> None:
        self._package_directory = self._resolve_package_directory(package_directory)

    @staticmethod
    def _resolve_package_directory(package_directory: Path) -> Path:
        frozen_root = getattr(sys, "_MEIPASS", None)
        if isinstance(frozen_root, str) and frozen_root:
            return (Path(frozen_root) / "app" / "presentation").resolve()
        return package_directory.resolve()

    @property
    def styles_directory(self) -> Path:
        return self._package_directory / "styles"

    @property
    def resources_directory(self) -> Path:
        return self._package_directory / "resources"

    @property
    def icons_directory(self) -> Path:
        return self.resources_directory / "icons"

    def style_path(self, theme_name: str) -> Path:
        return self.styles_directory / f"{theme_name}.qss"

    def icon_path(self, icon_name: str) -> Path:
        return self.icons_directory / icon_name

    def application_icon_path(self) -> Path:
        return self.icon_path("app_icon.svg")

    def splash_path(self) -> Path:
        return self.resources_directory / "splash.svg"
