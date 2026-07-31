from pathlib import Path

from PySide6.QtGui import QPixmap

from app.presentation.resource_manager import ResourceManager
from app.presentation.splash_screen import SplashScreen


def test_splash_screen_uses_managed_pixmap(
    qtbot,
    tmp_path: Path,
) -> None:
    resources = tmp_path / "resources"
    resources.mkdir()
    pixmap = QPixmap(20, 10)
    assert pixmap.save(str(resources / "splash.svg"), "PNG")
    manager = ResourceManager(tmp_path)

    splash = SplashScreen(manager)
    qtbot.addWidget(splash)

    assert splash.objectName() == "splashScreen"
    assert splash.pixmap().size().width() == 20
    assert splash.pixmap().size().height() == 10
