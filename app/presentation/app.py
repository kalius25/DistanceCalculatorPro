import os
import sys
from pathlib import Path
from typing import cast

from PySide6.QtCore import QSettings, QTimer
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication, QMessageBox

from app.configuration.configuration_loader import ConfigurationLoader
from app.configuration.models import AppConfig
from app.diagnostics import DiagnosticsManager, DiagnosticsSettings
from app.engines.bing_maps_engine import BingMapsEngine
from app.engines.browser_manager import BrowserManager
from app.engines.google_maps_engine import GoogleMapsEngine
from app.engines.google_maps_locator import GoogleMapsLocator
from app.engines.openstreetmap_engine import OpenStreetMapEngine
from app.enums.provider_type import ProviderType
from app.logging.logging_manager import LoggingManager
from app.parsers.google_maps_parser import GoogleMapsParser
from app.providers.bing_web_provider import BingWebProvider
from app.providers.google_web_provider import GoogleWebProvider
from app.providers.openstreetmap_web_provider import (
    OpenStreetMapWebProvider,
)
from app.providers.provider_router import ProviderRouter
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
from .startup import StartupValidationError, StartupValidator
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
    google_provider = GoogleWebProvider(
        browser_manager,
        maps_engine,
        diagnostics=diagnostics,
    )
    bing_provider = BingWebProvider(
        browser_manager,
        BingMapsEngine(configuration.browser.timeout, diagnostics),
        diagnostics=diagnostics,
    )
    osm_provider = OpenStreetMapWebProvider(
        browser_manager,
        OpenStreetMapEngine(configuration.browser.timeout, diagnostics),
        diagnostics=diagnostics,
    )
    provider = ProviderRouter(
        {
            ProviderType.GOOGLE_MAPS_WEB: google_provider,
            ProviderType.BING_MAPS_WEB: bing_provider,
            ProviderType.OPENSTREETMAP_WEB: osm_provider,
        }
    )
    calculation_service = CalculationService(provider)
    batch_service = BatchCalculationService(calculation_service)
    return CalculationExecutionCoordinator(
        CalculationJobBuilder(),
        batch_service,
        shutdown_callback=browser_manager.close,
    )


def create_application() -> tuple[
    QApplication,
    MainWindow,
    ExceptionHandler,
    SplashScreen,
]:
    metadata = AppMetadata()
    configuration = ConfigurationLoader.load()
    StartupValidator().validate(configuration)
    LoggingManager.configure(configuration.logging)
    logger = LoggingManager.get_logger("presentation")

    application = QApplication(sys.argv)
    application.setApplicationName(metadata.name)
    application.setApplicationVersion(metadata.version)
    application.setOrganizationName(metadata.organization)
    application.setOrganizationDomain(metadata.domain)

    package_directory = Path(__file__).resolve().parent
    resource_manager = ResourceManager(package_directory)
    application.setWindowIcon(QIcon(str(resource_manager.application_icon_path())))

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



def _write_smoke_stage(stage: str) -> None:
    status_file = os.getenv("DCP_SMOKE_STATUS_FILE", "").strip()
    if not status_file:
        return

    try:
        Path(status_file).write_text(stage, encoding="utf-8")
    except OSError:
        pass

def _schedule_smoke_exit(application: QApplication) -> None:
    raw_delay = os.getenv("DCP_SMOKE_EXIT_MS", "").strip()
    if not raw_delay:
        return

    try:
        delay_ms = int(raw_delay)
    except ValueError:
        return

    if delay_ms <= 0:
        return

    QTimer.singleShot(delay_ms, application.quit)


def main() -> int:
    main_window: MainWindow | None = None
    exception_handler: ExceptionHandler | None = None
    try:
        _write_smoke_stage("before create_application")
        application, main_window, exception_handler, splash_screen = (
            create_application()
        )
        _write_smoke_stage("after create_application")
        main_window.show()
        _write_smoke_stage("after main_window.show")
        splash_screen.finish(main_window)
        _write_smoke_stage("before event loop")
        _schedule_smoke_exit(application)
        result = application.exec()
        _write_smoke_stage("after event loop")
        return result
    except StartupValidationError as error:
        existing_application = QApplication.instance()

        if existing_application is not None:
            application = cast(
                QApplication,
                existing_application,
            )
        else:
            application = QApplication(sys.argv)

        QMessageBox.critical(
            None,
            "Unable to start DistanceCalculatorPro",
            str(error),
        )
        return 1
    finally:
        if main_window is not None:
            main_window.shutdown()
        if exception_handler is not None:
            exception_handler.restore()
        LoggingManager.reset()


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
