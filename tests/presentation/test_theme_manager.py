from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.presentation.resource_manager import ResourceManager
from app.presentation.theme_manager import ThemeManager


@pytest.fixture
def resource_manager(tmp_path: Path) -> ResourceManager:
    return ResourceManager(tmp_path)


def test_constructor_defaults_to_light_theme(
    resource_manager: ResourceManager,
) -> None:
    manager = ThemeManager(resource_manager)

    assert manager.current_theme == "light"


def test_apply_theme_normalizes_name_and_applies_stylesheet(
    resource_manager: ResourceManager,
) -> None:
    resource_manager.styles_directory.mkdir(parents=True)
    resource_manager.style_path("dark").write_text(
        "QWidget { color: white; }",
        encoding="utf-8",
    )
    application = MagicMock()
    manager = ThemeManager(resource_manager)

    manager.apply_theme(application, "  DARK ")

    application.setStyleSheet.assert_called_once_with(
        "QWidget { color: white; }"
    )
    assert manager.current_theme == "dark"


def test_apply_theme_rejects_unsupported_theme(
    resource_manager: ResourceManager,
) -> None:
    manager = ThemeManager(resource_manager)

    with pytest.raises(
        ValueError,
        match=(
            "Unsupported theme 'blue'. Supported themes: light, dark."
        ),
    ):
        manager.apply_theme(MagicMock(), "blue")


def test_apply_theme_raises_when_file_is_missing(
    resource_manager: ResourceManager,
) -> None:
    manager = ThemeManager(resource_manager)
    expected_path = resource_manager.style_path("light")

    with pytest.raises(
        FileNotFoundError,
        match=f"Theme file not found: {expected_path}",
    ):
        manager.apply_theme(MagicMock(), "light")
