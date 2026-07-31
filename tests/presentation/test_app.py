from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

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
            "MainWindow",
            return_value=main_window,
        ) as window_type,
    ):
        theme_type.SUPPORTED_THEMES = ("light", "dark")
        result = app_module.create_application()

    metadata = app_module.AppMetadata()
    configure.assert_called_once_with(configuration.logging)
    get_logger.assert_called_once_with("presentation")
    application_type.assert_called_once_with(app_module.sys.argv)
    application.setApplicationName.assert_called_once_with(metadata.name)
    application.setApplicationVersion.assert_called_once_with(metadata.version)
    application.setOrganizationName.assert_called_once_with(
        metadata.organization
    )
    application.setOrganizationDomain.assert_called_once_with(metadata.domain)
    resource_type.assert_called_once_with(
        Path(app_module.__file__).resolve().parent
    )
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
    exception_handler.install.assert_called_once_with()
    window_type.assert_called_once_with(
        application=application,
        metadata=metadata,
        theme_manager=theme_manager,
        settings_manager=settings_manager,
        workbook_inspector="workbook_inspector",
    )
    logger.info.assert_called_once_with(
        "Presentation application initialized"
    )
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

    exception_handler.restore.assert_called_once_with()
    reset.assert_called_once_with()
