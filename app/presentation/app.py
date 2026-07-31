import sys
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.configuration.configuration_loader import ConfigurationLoader
from app.logging.logging_manager import LoggingManager
from app.workbooks import (
    CsvWorkbookReader,
    OpenPyXLWorkbookReader,
    WorkbookInspectorService,
)

from .app_metadata import AppMetadata
from .exception_handler import ExceptionHandler
from .main_window import MainWindow
from .resource_manager import ResourceManager
from .settings_manager import SettingsManager
from .splash_screen import SplashScreen
from .theme_manager import ThemeManager


def create_application() -> tuple[
    QApplication,
    MainWindow,
    ExceptionHandler,
    SplashScreen,
]:
    metadata = AppMetadata()
    configuration = ConfigurationLoader.load()
    LoggingManager.configure(configuration.logging)
    logger = LoggingManager.get_logger("presentation")

    application = QApplication(sys.argv)
    application.setApplicationName(metadata.name)
    application.setApplicationVersion(metadata.version)
    application.setOrganizationName(metadata.organization)
    application.setOrganizationDomain(metadata.domain)

    package_directory = Path(__file__).resolve().parent
    resource_manager = ResourceManager(package_directory)
    application.setWindowIcon(
        QIcon(str(resource_manager.application_icon_path()))
    )

    splash_screen = SplashScreen(resource_manager)
    splash_screen.show()
    application.processEvents()

    settings_manager = SettingsManager(QSettings())
    theme_manager = ThemeManager(resource_manager)

    saved_theme = settings_manager.theme_name()
    if saved_theme not in ThemeManager.SUPPORTED_THEMES:
        logger.warning("Unsupported saved theme '%s'; using light", saved_theme)
        saved_theme = "light"
    theme_manager.apply_theme(application, saved_theme)

    exception_handler = ExceptionHandler(logger)
    exception_handler.install()

    workbook_inspector = WorkbookInspectorService(
        (OpenPyXLWorkbookReader(), CsvWorkbookReader())
    )
    main_window = MainWindow(
        application=application,
        metadata=metadata,
        theme_manager=theme_manager,
        settings_manager=settings_manager,
        workbook_inspector=workbook_inspector,
    )
    logger.info("Presentation application initialized")
    return application, main_window, exception_handler, splash_screen


def main() -> int:
    application, main_window, exception_handler, splash_screen = (
        create_application()
    )
    main_window.show()
    splash_screen.finish(main_window)
    try:
        return application.exec()
    finally:
        exception_handler.restore()
        LoggingManager.reset()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
