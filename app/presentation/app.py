import sys
from pathlib import Path

from PySide6.QtCore import QSettings
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from app.configuration.configuration_loader import ConfigurationLoader
from app.configuration.models import AppConfig
from app.diagnostics import DiagnosticsManager, DiagnosticsSettings
from app.engines.browser_manager import BrowserManager
from app.engines.google_maps_engine import GoogleMapsEngine
from app.engines.google_maps_locator import GoogleMapsLocator
from app.logging.logging_manager import LoggingManager
from app.parsers.google_maps_parser import GoogleMapsParser
from app.providers.google_web_provider import GoogleWebProvider
from app.services.batch_calculation_service import BatchCalculationService
from app.services.calculation_service import CalculationService
from app.workbooks import (
    CsvWorkbookReader,
    OpenPyXLWorkbookReader,
    WorkbookInspectorService,
)

from .app_metadata import AppMetadata
from .exception_handler import ExceptionHandler
from .execution import CalculationExecutionCoordinator, CalculationJobBuilder
from .main_window import MainWindow
from .resource_manager import ResourceManager
from .settings_manager import SettingsManager
from .splash_screen import SplashScreen
from .theme_manager import ThemeManager


def create_execution_coordinator(
    configuration: AppConfig,
    diagnostics_manager: DiagnosticsManager | None = None,
) -> CalculationExecutionCoordinator:
    """Compose the route-calculation execution dependency tree."""
    diagnostics = diagnostics_manager or DiagnosticsManager()
    browser_manager = BrowserManager(configuration.browser)
    parser = GoogleMapsParser()
    maps_engine = GoogleMapsEngine(
        configuration.google_maps,
        GoogleMapsLocator(),
        parser,
        diagnostics,
    )
    provider = GoogleWebProvider(browser_manager, maps_engine)
    calculation_service = CalculationService(provider)
    batch_service = BatchCalculationService(calculation_service)
    return CalculationExecutionCoordinator(
        CalculationJobBuilder(),
        batch_service,
    )


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

    diagnostics_manager = DiagnosticsManager(
        DiagnosticsSettings(
            enabled=settings_manager.debug_enabled(),
            trace_browser=settings_manager.trace_browser(),
            parser_diagnostics=settings_manager.parser_diagnostics(),
            save_html=settings_manager.save_html(),
            save_screenshot=settings_manager.save_screenshot(),
            save_json=settings_manager.save_json(),
        )
    )
    execution_coordinator = create_execution_coordinator(
        configuration, diagnostics_manager
    )

    main_window = MainWindow(
        application=application,
        metadata=metadata,
        theme_manager=theme_manager,
        settings_manager=settings_manager,
        workbook_inspector=workbook_inspector,
        execution_coordinator=execution_coordinator,
        diagnostics_manager=diagnostics_manager,
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
