from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtWidgets import QApplication

from app.presentation import app as app_module


def _application_dependencies(saved_theme: str = "light") -> tuple[
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
    MagicMock,
]:
    application = MagicMock()
    resource_manager = MagicMock()
    resource_manager.application_icon_path.return_value = Path("app.ico")
    splash_screen = MagicMock()
    settings_manager = MagicMock()
    settings_manager.theme_name.return_value = saved_theme
    settings_manager.debug_enabled.return_value = False
    settings_manager.trace_browser.return_value = False
    settings_manager.parser_diagnostics.return_value = False
    settings_manager.save_html.return_value = False
    settings_manager.save_screenshot.return_value = False
    settings_manager.save_json.return_value = False
    theme_manager = MagicMock()
    exception_handler = MagicMock()
    return (
        application,
        resource_manager,
        splash_screen,
        settings_manager,
        theme_manager,
        exception_handler,
    )


def test_create_application_composes_and_initializes_shell() -> None:
    (
        application,
        resource_manager,
        splash_screen,
        settings_manager,
        theme_manager,
        exception_handler,
    ) = _application_dependencies()
    configuration = MagicMock()
    logger = MagicMock()
    main_window = MagicMock()

    with (
        patch.object(
            app_module.ConfigurationLoader,
            "load",
            return_value=configuration,
        ),
        patch.object(app_module, "StartupValidator") as validator_type,
        patch.object(app_module.LoggingManager, "configure") as configure,
        patch.object(
            app_module.LoggingManager,
            "get_logger",
            return_value=logger,
        ) as get_logger,
        patch.object(
            app_module,
            "QApplication",
            return_value=application,
        ) as application_type,
        patch.object(app_module, "QIcon", return_value="icon") as icon_type,
        patch.object(
            app_module,
            "ResourceManager",
            return_value=resource_manager,
        ) as resource_type,
        patch.object(
            app_module,
            "SplashScreen",
            return_value=splash_screen,
        ) as splash_type,
        patch.object(app_module, "QSettings", return_value="qsettings"),
        patch.object(
            app_module,
            "SettingsManager",
            return_value=settings_manager,
        ) as settings_type,
        patch.object(
            app_module,
            "ThemeManager",
            return_value=theme_manager,
        ) as theme_type,
        patch.object(
            app_module,
            "ExceptionHandler",
            return_value=exception_handler,
        ) as handler_type,
        patch.object(app_module, "OpenPyXLWorkbookReader", return_value="excel_reader"),
        patch.object(app_module, "CsvWorkbookReader", return_value="csv_reader"),
        patch.object(
            app_module,
            "WorkbookInspectorService",
            return_value="workbook_inspector",
        ) as inspector_type,
        patch.object(
            app_module,
            "create_execution_coordinator",
            return_value="execution_coordinator",
        ) as create_execution_coordinator,
        patch.object(
            app_module,
            "DiagnosticsManager",
            return_value="diagnostics_manager",
        ) as diagnostics_type,
        patch.object(
            app_module,
            "MainWindow",
            return_value=main_window,
        ) as window_type,
    ):
        theme_type.SUPPORTED_THEMES = ("light", "dark")
        result = app_module.create_application()

    metadata = app_module.AppMetadata()
    validator_type.return_value.validate.assert_called_once_with(
        configuration,
        validate_browser=True,
    )
    configure.assert_called_once_with(configuration.logging)
    get_logger.assert_called_once_with("presentation")
    application_type.assert_called_once_with(app_module.sys.argv)
    application.setApplicationName.assert_called_once_with(metadata.name)
    application.setApplicationVersion.assert_called_once_with(metadata.version)
    application.setOrganizationName.assert_called_once_with(metadata.organization)
    application.setOrganizationDomain.assert_called_once_with(metadata.domain)
    resource_type.assert_called_once_with(Path(app_module.__file__).resolve().parent)
    icon_type.assert_called_once_with("app.ico")
    application.setWindowIcon.assert_called_once_with("icon")
    splash_type.assert_called_once_with(resource_manager)
    splash_screen.show.assert_called_once_with()
    application.processEvents.assert_called_once_with()
    settings_type.assert_called_once_with("qsettings")
    theme_type.assert_called_once_with(resource_manager)
    theme_manager.apply_theme.assert_called_once_with(application, "light")
    handler_type.assert_called_once_with(logger)
    inspector_type.assert_called_once_with(("excel_reader", "csv_reader"))
    diagnostics_type.assert_called_once()
    create_execution_coordinator.assert_called_once_with(
        configuration, "diagnostics_manager"
    )
    exception_handler.install.assert_called_once_with()
    window_type.assert_called_once_with(
        application=application,
        metadata=metadata,
        theme_manager=theme_manager,
        settings_manager=settings_manager,
        workbook_inspector="workbook_inspector",
        execution_coordinator="execution_coordinator",
        diagnostics_manager="diagnostics_manager",
    )
    logger.info.assert_called_once_with("Presentation application initialized")
    assert result == (
        application,
        main_window,
        exception_handler,
        splash_screen,
    )


def test_create_application_replaces_unsupported_saved_theme() -> None:
    (
        application,
        resource_manager,
        splash_screen,
        settings_manager,
        theme_manager,
        exception_handler,
    ) = _application_dependencies("unsupported")
    configuration = MagicMock()
    logger = MagicMock()

    with (
        patch.object(
            app_module.ConfigurationLoader,
            "load",
            return_value=configuration,
        ),
        patch.object(app_module, "StartupValidator"),
        patch.object(app_module.LoggingManager, "configure"),
        patch.object(
            app_module.LoggingManager,
            "get_logger",
            return_value=logger,
        ),
        patch.object(app_module, "QApplication", return_value=application),
        patch.object(app_module, "QIcon"),
        patch.object(
            app_module,
            "ResourceManager",
            return_value=resource_manager,
        ),
        patch.object(
            app_module,
            "SplashScreen",
            return_value=splash_screen,
        ),
        patch.object(app_module, "QSettings"),
        patch.object(
            app_module,
            "SettingsManager",
            return_value=settings_manager,
        ),
        patch.object(
            app_module,
            "ThemeManager",
            return_value=theme_manager,
        ) as theme_type,
        patch.object(
            app_module,
            "ExceptionHandler",
            return_value=exception_handler,
        ),
        patch.object(app_module, "create_execution_coordinator"),
        patch.object(app_module, "MainWindow"),
    ):
        theme_type.SUPPORTED_THEMES = ("light", "dark")
        app_module.create_application()

    logger.warning.assert_called_once_with(
        "Unsupported saved theme '%s'; using light",
        "unsupported",
    )
    theme_manager.apply_theme.assert_called_once_with(application, "light")


def test_main_runs_event_loop_and_always_cleans_up() -> None:
    application = MagicMock()
    application.exec.return_value = 17
    main_window = MagicMock()
    exception_handler = MagicMock()
    splash_screen = MagicMock()

    with (
        patch.object(
            app_module,
            "create_application",
            return_value=(
                application,
                main_window,
                exception_handler,
                splash_screen,
            ),
        ),
        patch.object(app_module.LoggingManager, "reset") as reset,
    ):
        result = app_module.main()

    main_window.show.assert_called_once_with()
    splash_screen.finish.assert_called_once_with(main_window)
    application.exec.assert_called_once_with()
    main_window.shutdown.assert_called_once_with()
    exception_handler.restore.assert_called_once_with()
    reset.assert_called_once_with()
    assert result == 17


def test_main_cleans_up_when_event_loop_raises() -> None:
    application = MagicMock()
    application.exec.side_effect = RuntimeError("event loop failed")
    main_window = MagicMock()
    exception_handler = MagicMock()
    splash_screen = MagicMock()

    with (
        patch.object(
            app_module,
            "create_application",
            return_value=(
                application,
                main_window,
                exception_handler,
                splash_screen,
            ),
        ),
        patch.object(app_module.LoggingManager, "reset") as reset,
        pytest.raises(RuntimeError, match="event loop failed"),
    ):
        app_module.main()

    main_window.shutdown.assert_called_once_with()
    exception_handler.restore.assert_called_once_with()
    reset.assert_called_once_with()


def test_create_execution_coordinator_composes_calculation_tree() -> None:
    configuration = MagicMock()
    browser = MagicMock()
    locator = MagicMock()
    parser = MagicMock()
    engine = MagicMock()
    provider = MagicMock()
    calculation_service = MagicMock()
    batch_service = MagicMock()
    builder = MagicMock()
    coordinator = MagicMock()
    diagnostics = MagicMock()

    with (
        patch.object(
            app_module,
            "BrowserManager",
            return_value=browser,
        ) as browser_type,
        patch.object(app_module, "GoogleMapsLocator", return_value=locator),
        patch.object(app_module, "GoogleMapsParser", return_value=parser),
        patch.object(
            app_module,
            "GoogleMapsEngine",
            return_value=engine,
        ) as engine_type,
        patch.object(
            app_module,
            "GoogleWebProvider",
            return_value=provider,
        ) as provider_type,
        patch.object(
            app_module,
            "CalculationService",
            return_value=calculation_service,
        ) as calculation_type,
        patch.object(
            app_module,
            "BatchCalculationService",
            return_value=batch_service,
        ) as batch_type,
        patch.object(app_module, "CalculationJobBuilder", return_value=builder),
        patch.object(
            app_module,
            "CalculationExecutionCoordinator",
            return_value=coordinator,
        ) as coordinator_type,
    ):
        result = app_module.create_execution_coordinator(configuration, diagnostics)

    browser_type.assert_called_once_with(configuration.browser)
    engine_type.assert_called_once_with(
        configuration.google_maps, locator, parser, diagnostics
    )
    provider_type.assert_called_once_with(
        browser,
        engine,
        diagnostics=diagnostics,
    )
    calculation_type.assert_called_once_with(provider)
    batch_type.assert_called_once_with(calculation_service)
    coordinator_type.assert_called_once_with(
        builder,
        batch_service,
        shutdown_callback=browser.close,
    )
    assert result is coordinator


def test_main_reports_startup_validation_failure(
    qapp: QApplication,
) -> None:
    from app.presentation.startup import (
        StartupIssue,
        StartupValidationError,
    )

    error = StartupValidationError(
        (
            StartupIssue(
                "Chromium",
                "missing",
            ),
        )
    )

    with (
        patch.object(
            app_module,
            "create_application",
            side_effect=error,
        ),
        patch.object(
            app_module.QApplication,
            "instance",
            return_value=qapp,
        ),
        patch.object(
            app_module.QMessageBox,
            "critical",
        ) as critical,
        patch.object(
            app_module.LoggingManager,
            "reset",
        ) as reset,
    ):
        result = app_module.main()

    assert result == 1

    critical.assert_called_once_with(
        None,
        "Unable to start DistanceCalculatorPro",
        str(error),
    )
    reset.assert_called_once_with()


def test_main_creates_application_to_report_early_startup_failure() -> None:
    from app.presentation.startup import (
        StartupIssue,
        StartupValidationError,
    )

    error = StartupValidationError(
        (
            StartupIssue(
                "Output",
                "not writable",
            ),
        )
    )
    application = MagicMock()

    with (
        patch.object(
            app_module,
            "create_application",
            side_effect=error,
        ),
        patch.object(
            app_module,
            "QApplication",
        ) as application_type,
        patch.object(
            app_module.QMessageBox,
            "critical",
        ) as critical,
        patch.object(
            app_module.LoggingManager,
            "reset",
        ) as reset,
    ):
        application_type.instance.return_value = None
        application_type.return_value = application

        result = app_module.main()

    assert result == 1

    application_type.assert_called_once_with(sys.argv)
    critical.assert_called_once_with(
        None,
        "Unable to start DistanceCalculatorPro",
        str(error),
    )
    reset.assert_called_once_with()


def test_schedule_smoke_exit_ignores_missing_delay(monkeypatch) -> None:
    application = MagicMock()
    monkeypatch.delenv("DCP_SMOKE_EXIT_MS", raising=False)

    with patch.object(app_module.QTimer, "singleShot") as single_shot:
        app_module._schedule_smoke_exit(application)

    single_shot.assert_not_called()


@pytest.mark.parametrize("raw_delay", ["bad", "0", "-5"])
def test_schedule_smoke_exit_ignores_invalid_delay(
    monkeypatch,
    raw_delay: str,
) -> None:
    application = MagicMock()
    monkeypatch.setenv("DCP_SMOKE_EXIT_MS", raw_delay)

    with patch.object(app_module.QTimer, "singleShot") as single_shot:
        app_module._schedule_smoke_exit(application)

    single_shot.assert_not_called()


def test_schedule_smoke_exit_schedules_positive_delay(monkeypatch) -> None:
    application = MagicMock()
    monkeypatch.setenv("DCP_SMOKE_EXIT_MS", "1250")

    with patch.object(app_module.QTimer, "singleShot") as single_shot:
        app_module._schedule_smoke_exit(application)

    single_shot.assert_called_once_with(1250, application.quit)


def test_main_schedules_smoke_exit_before_event_loop() -> None:
    application = MagicMock()
    application.exec.return_value = 0
    main_window = MagicMock()
    exception_handler = MagicMock()
    splash_screen = MagicMock()

    with (
        patch.object(
            app_module,
            "create_application",
            return_value=(
                application,
                main_window,
                exception_handler,
                splash_screen,
            ),
        ),
        patch.object(app_module, "_schedule_smoke_exit") as schedule,
        patch.object(app_module.LoggingManager, "reset"),
    ):
        result = app_module.main()

    assert result == 0
    schedule.assert_called_once_with(application)


def test_write_smoke_stage_ignores_missing_status_file(monkeypatch) -> None:
    monkeypatch.delenv("DCP_SMOKE_STATUS_FILE", raising=False)

    app_module._write_smoke_stage("stage")


def test_write_smoke_stage_writes_status_file(
    tmp_path,
    monkeypatch,
) -> None:
    status_file = tmp_path / "smoke.txt"
    monkeypatch.setenv("DCP_SMOKE_STATUS_FILE", str(status_file))

    app_module._write_smoke_stage("before event loop")

    assert status_file.read_text(encoding="utf-8") == "before event loop"


def test_write_smoke_stage_ignores_write_error(monkeypatch) -> None:
    monkeypatch.setenv("DCP_SMOKE_STATUS_FILE", "status.txt")

    with patch.object(app_module.Path, "write_text", side_effect=OSError):
        app_module._write_smoke_stage("stage")


def test_is_executable_smoke_requires_explicit_flag(monkeypatch) -> None:
    monkeypatch.delenv("DCP_EXECUTABLE_SMOKE", raising=False)
    assert not app_module._is_executable_smoke()

    monkeypatch.setenv("DCP_EXECUTABLE_SMOKE", "0")
    assert not app_module._is_executable_smoke()

    monkeypatch.setenv("DCP_EXECUTABLE_SMOKE", "1")
    assert app_module._is_executable_smoke()


def test_create_application_skips_browser_validation_in_executable_smoke(
    monkeypatch,
) -> None:
    configuration = MagicMock()
    validator = MagicMock()
    monkeypatch.setenv("DCP_EXECUTABLE_SMOKE", "1")

    with (
        patch.object(
            app_module.ConfigurationLoader,
            "load",
            return_value=configuration,
        ),
        patch.object(
            app_module,
            "StartupValidator",
            return_value=validator,
        ),
        patch.object(
            app_module.LoggingManager,
            "configure",
            side_effect=RuntimeError("stop after validation"),
        ),
        pytest.raises(RuntimeError, match="stop after validation"),
    ):
        app_module.create_application()

    validator.validate.assert_called_once_with(
        configuration,
        validate_browser=False,
    )


def test_create_application_requires_browser_validation_normally(
    monkeypatch,
) -> None:
    configuration = MagicMock()
    validator = MagicMock()
    monkeypatch.delenv("DCP_EXECUTABLE_SMOKE", raising=False)

    with (
        patch.object(
            app_module.ConfigurationLoader,
            "load",
            return_value=configuration,
        ),
        patch.object(
            app_module,
            "StartupValidator",
            return_value=validator,
        ),
        patch.object(
            app_module.LoggingManager,
            "configure",
            side_effect=RuntimeError("stop after validation"),
        ),
        pytest.raises(RuntimeError, match="stop after validation"),
    ):
        app_module.create_application()

    validator.validate.assert_called_once_with(
        configuration,
        validate_browser=True,
    )
