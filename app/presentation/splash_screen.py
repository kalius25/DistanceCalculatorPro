from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen

from .resource_manager import ResourceManager


class SplashScreen(QSplashScreen):
    """Displays the lightweight application startup screen."""

    def __init__(self, resource_manager: ResourceManager) -> None:
        pixmap = QPixmap(str(resource_manager.splash_path()))
        super().__init__(pixmap)
        self.setObjectName("splashScreen")
