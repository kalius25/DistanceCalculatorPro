from pathlib import Path

from app.presentation.resource_manager import ResourceManager


def test_resolves_all_resource_paths(tmp_path: Path) -> None:
    package_directory = tmp_path / "package"
    manager = ResourceManager(package_directory)
    resolved = package_directory.resolve()

    assert manager.styles_directory == resolved / "styles"
    assert manager.resources_directory == resolved / "resources"
    assert manager.icons_directory == resolved / "resources" / "icons"
    assert manager.style_path("dark") == resolved / "styles" / "dark.qss"
    assert manager.icon_path("open.svg") == (
        resolved / "resources" / "icons" / "open.svg"
    )
    assert manager.application_icon_path() == (
        resolved / "resources" / "icons" / "app_icon.svg"
    )
    assert manager.splash_path() == resolved / "resources" / "splash.svg"


def test_resource_manager_uses_pyinstaller_meipass(
    tmp_path: Path,
    monkeypatch,
) -> None:
    import sys

    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)

    manager = ResourceManager(Path("ignored"))

    assert (
        manager.styles_directory
        == (tmp_path / "app" / "presentation" / "styles").resolve()
    )
