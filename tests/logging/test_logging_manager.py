from __future__ import annotations

import logging
from pathlib import Path

import pytest

from app.configuration.models import LoggingConfig
from app.logging import LoggingManager
from app.logging.config import LOGGER_NAME
from app.logging.formatter import StructuredJsonFormatter


@pytest.fixture(autouse=True)
def reset_logging_manager():
    """
    Isolate LoggingManager state between tests.

    LoggingManager.reset() removes only managed handlers.
    External handlers owned by pytest or other integrations remain intact.
    """

    LoggingManager.reset()

    yield

    LoggingManager.reset()


def create_logging_config(
    directory: Path,
    *,
    level: str = "INFO",
    filename: str = "test.log",
) -> LoggingConfig:
    return LoggingConfig(
        level=level,
        directory=str(directory),
        filename=filename,
    )


def get_application_logger() -> logging.Logger:
    return logging.getLogger(LOGGER_NAME)


def get_managed_handlers() -> list[logging.Handler]:
    application_logger = get_application_logger()

    return [
        handler
        for handler in application_logger.handlers
        if getattr(
            handler,
            LoggingManager._MANAGED_HANDLER_ATTRIBUTE,
            False,
        )
    ]


def get_external_handlers() -> list[logging.Handler]:
    application_logger = get_application_logger()

    return [
        handler
        for handler in application_logger.handlers
        if not getattr(
            handler,
            LoggingManager._MANAGED_HANDLER_ATTRIBUTE,
            False,
        )
    ]


def test_configure_stores_logging_config(
    tmp_path: Path,
):
    config = create_logging_config(tmp_path)

    LoggingManager.configure(config)

    assert LoggingManager._config == config
    assert LoggingManager._initialized is False
    assert LoggingManager._root_logger is None


def test_configure_same_config_does_not_reset_initialized_state(
    tmp_path: Path,
):
    config = create_logging_config(tmp_path)

    LoggingManager.configure(config)
    LoggingManager.get_logger("first")

    original_root_logger = LoggingManager._root_logger
    original_handlers = list(get_managed_handlers())

    LoggingManager.configure(config)

    assert LoggingManager._initialized is True
    assert LoggingManager._root_logger is original_root_logger
    assert get_managed_handlers() == original_handlers


def test_configure_different_config_resets_manager(
    tmp_path: Path,
):
    first_config = create_logging_config(
        tmp_path / "first",
        filename="first.log",
    )
    second_config = create_logging_config(
        tmp_path / "second",
        filename="second.log",
    )

    LoggingManager.configure(first_config)
    LoggingManager.get_logger("first")

    assert len(get_managed_handlers()) == 2

    LoggingManager.configure(second_config)

    assert LoggingManager._config == second_config
    assert LoggingManager._initialized is False
    assert LoggingManager._root_logger is None
    assert get_managed_handlers() == []


def test_get_logger_returns_application_child_logger(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(tmp_path)
    )

    logger = LoggingManager.get_logger(
        "test-module",
    )

    assert logger.name == (
        f"{LOGGER_NAME}.test-module"
    )


def test_get_logger_initializes_application_logger(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(tmp_path)
    )

    LoggingManager.get_logger("module")

    application_logger = get_application_logger()

    assert LoggingManager._initialized is True
    assert LoggingManager._root_logger is application_logger
    assert application_logger.propagate is False


def test_repeated_get_logger_returns_existing_root_logger(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(tmp_path)
    )

    first_logger = LoggingManager.get_logger("first")
    root_logger = LoggingManager._root_logger

    second_logger = LoggingManager.get_logger("second")

    assert LoggingManager._root_logger is root_logger
    assert first_logger.parent is root_logger
    assert second_logger.parent is root_logger


def test_logging_manager_uses_configured_level(
    tmp_path: Path,
):
    config = create_logging_config(
        tmp_path,
        level="DEBUG",
    )

    LoggingManager.configure(config)
    LoggingManager.get_logger("module")

    assert (
        get_application_logger().level
        == logging.DEBUG
    )


def test_logging_manager_accepts_lowercase_level(
    tmp_path: Path,
):
    config = create_logging_config(
        tmp_path,
        level="warning",
    )

    LoggingManager.configure(config)
    LoggingManager.get_logger("module")

    assert (
        get_application_logger().level
        == logging.WARNING
    )


def test_logging_manager_creates_log_directory(
    tmp_path: Path,
):
    log_directory = (
        tmp_path / "nested" / "logs"
    )

    LoggingManager.configure(
        create_logging_config(log_directory)
    )
    LoggingManager.get_logger("module")

    assert log_directory.is_dir()


def test_logging_manager_creates_two_managed_handlers(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(
            tmp_path,
            filename="application.log",
        )
    )

    LoggingManager.get_logger("module")

    managed_handlers = get_managed_handlers()

    assert len(managed_handlers) == 2


def test_logging_manager_creates_console_handler(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(tmp_path)
    )

    LoggingManager.get_logger("module")

    console_handlers = [
        handler
        for handler in get_managed_handlers()
        if type(handler) is logging.StreamHandler
    ]

    assert len(console_handlers) == 1


def test_logging_manager_creates_file_handler(
    tmp_path: Path,
):
    log_filename = "application.log"

    LoggingManager.configure(
        create_logging_config(
            tmp_path,
            filename=log_filename,
        )
    )

    LoggingManager.get_logger("module")

    file_handlers = [
        handler
        for handler in get_managed_handlers()
        if isinstance(
            handler,
            logging.FileHandler,
        )
    ]

    assert len(file_handlers) == 1
    assert file_handlers[0].baseFilename == str(
        tmp_path / log_filename
    )


def test_managed_handlers_use_structured_json_formatter(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(tmp_path)
    )

    LoggingManager.get_logger("module")

    managed_handlers = get_managed_handlers()

    assert managed_handlers

    assert all(
        isinstance(
            handler.formatter,
            StructuredJsonFormatter,
        )
        for handler in managed_handlers
    )


def test_repeated_get_logger_does_not_duplicate_managed_handlers(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(tmp_path)
    )

    LoggingManager.get_logger("first")
    original_handlers = list(
        get_managed_handlers()
    )

    LoggingManager.get_logger("second")

    assert get_managed_handlers() == original_handlers
    assert len(get_managed_handlers()) == 2


def test_external_handler_is_preserved_during_initialization(
    tmp_path: Path,
):
    application_logger = get_application_logger()
    external_handler = logging.NullHandler()

    application_logger.addHandler(
        external_handler,
    )

    try:
        LoggingManager.configure(
            create_logging_config(tmp_path)
        )
        LoggingManager.get_logger("module")

        assert (
            external_handler
            in application_logger.handlers
        )
        assert len(get_managed_handlers()) == 2
    finally:
        application_logger.removeHandler(
            external_handler,
        )
        external_handler.close()


def test_configure_different_config_preserves_external_handler(
    tmp_path: Path,
):
    application_logger = get_application_logger()
    external_handler = logging.NullHandler()

    application_logger.addHandler(
        external_handler,
    )

    try:
        first_config = create_logging_config(
            tmp_path / "first",
            filename="first.log",
        )
        second_config = create_logging_config(
            tmp_path / "second",
            filename="second.log",
        )

        LoggingManager.configure(first_config)
        LoggingManager.get_logger("first")

        LoggingManager.configure(second_config)

        assert (
            external_handler
            in application_logger.handlers
        )
        assert get_managed_handlers() == []

        LoggingManager.get_logger("second")

        assert (
            external_handler
            in application_logger.handlers
        )
        assert len(get_managed_handlers()) == 2
    finally:
        LoggingManager.reset()

        application_logger.removeHandler(
            external_handler,
        )
        external_handler.close()


def test_reset_clears_manager_state(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(tmp_path)
    )
    LoggingManager.get_logger("module")

    LoggingManager.reset()

    assert LoggingManager._config is None
    assert LoggingManager._root_logger is None
    assert LoggingManager._initialized is False


def test_reset_removes_only_managed_handlers(
    tmp_path: Path,
):
    application_logger = get_application_logger()
    external_handler = logging.NullHandler()

    application_logger.addHandler(
        external_handler,
    )

    try:
        LoggingManager.configure(
            create_logging_config(tmp_path)
        )
        LoggingManager.get_logger("module")

        assert len(get_managed_handlers()) == 2

        LoggingManager.reset()

        assert get_managed_handlers() == []
        assert (
            external_handler
            in application_logger.handlers
        )
    finally:
        application_logger.removeHandler(
            external_handler,
        )
        external_handler.close()


def test_reset_preserves_pytest_external_handlers(
    tmp_path: Path,
):
    external_handlers_before = list(
        get_external_handlers()
    )

    LoggingManager.configure(
        create_logging_config(tmp_path)
    )
    LoggingManager.get_logger("module")

    LoggingManager.reset()

    external_handlers_after = (
        get_external_handlers()
    )

    assert external_handlers_after == (
        external_handlers_before
    )


def test_manager_uses_legacy_config_when_not_configured(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    """
    Preserve compatibility during dependency-tree migration.
    """

    fallback_config = LoggingConfig(
        level="WARNING",
        directory=str(tmp_path),
        filename="fallback.log",
    )

    monkeypatch.setattr(
        LoggingManager,
        "_get_effective_config",
        classmethod(
            lambda cls: fallback_config
        ),
    )

    logger = LoggingManager.get_logger(
        "fallback",
    )

    logger.warning(
        "Fallback logging test"
    )

    for handler in get_managed_handlers():
        handler.flush()

    assert logger.name == (
        f"{LOGGER_NAME}.fallback"
    )
    assert (
        get_application_logger().level
        == logging.WARNING
    )
    assert (
        tmp_path / "fallback.log"
    ).is_file()


def test_legacy_config_creates_managed_handlers(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    fallback_config = LoggingConfig(
        level="INFO",
        directory=str(tmp_path),
        filename="legacy.log",
    )

    monkeypatch.setattr(
        LoggingManager,
        "_get_effective_config",
        classmethod(
            lambda cls: fallback_config
        ),
    )

    LoggingManager.get_logger("legacy")

    assert len(get_managed_handlers()) == 2


def test_existing_managed_handlers_are_reused(
    tmp_path: Path,
):
    LoggingManager.configure(
        create_logging_config(tmp_path)
    )

    LoggingManager.get_logger("first")

    original_handlers = list(
        get_managed_handlers()
    )

    LoggingManager._initialized = False
    LoggingManager._root_logger = None

    LoggingManager.get_logger("second")

    assert get_managed_handlers() == original_handlers
    assert len(get_managed_handlers()) == 2