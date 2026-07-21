import logging
from unittest.mock import MagicMock
from unittest.mock import patch

from app.config import AppMode
from app.utils import logger


def test_create_formatter():
    formatter = logger._create_formatter()

    assert isinstance(formatter, logging.Formatter)

    record = logging.LogRecord(
        "test",
        logging.INFO,
        "",
        1,
        "hello",
        (),
        None,
    )

    text = formatter.format(record)

    assert "INFO" in text
    assert "hello" in text


def test_configure_root_logger_already_configured():
    root_logger = MagicMock()
    root_logger.handlers = [object()]

    with patch(
        "app.utils.logger.logging.getLogger",
        return_value=root_logger,
    ):
        logger._configure_root_logger()

    root_logger.setLevel.assert_not_called()
    root_logger.addHandler.assert_not_called()


def test_configure_root_logger_development():
    root_logger = MagicMock()
    root_logger.handlers = []

    file_handler = MagicMock()
    console_handler = MagicMock()

    with (
        patch(
            "app.utils.logger.logging.getLogger",
            return_value=root_logger,
        ),
        patch(
            "app.utils.logger.Path.mkdir",
        ) as mkdir,
        patch(
            "app.utils.logger.logging.FileHandler",
            return_value=file_handler,
        ) as file_cls,
        patch(
            "app.utils.logger.logging.StreamHandler",
            return_value=console_handler,
        ) as console_cls,
        patch(
            "app.utils.logger.APP_MODE",
            AppMode.DEVELOPMENT,
        ),
    ):
        logger._configure_root_logger()

    mkdir.assert_called_once()

    file_cls.assert_called_once()

    console_cls.assert_called_once()

    root_logger.setLevel.assert_called_once_with(logger.LOG_LEVEL)

    assert root_logger.addHandler.call_count == 2

    file_handler.setFormatter.assert_called_once()

    console_handler.setFormatter.assert_called_once()


def test_configure_root_logger_production():
    root_logger = MagicMock()
    root_logger.handlers = []

    file_handler = MagicMock()

    with (
        patch(
            "app.utils.logger.logging.getLogger",
            return_value=root_logger,
        ),
        patch("app.utils.logger.Path.mkdir"),
        patch(
            "app.utils.logger.logging.FileHandler",
            return_value=file_handler,
        ),
        patch(
            "app.utils.logger.logging.StreamHandler",
        ) as console_cls,
        patch(
            "app.utils.logger.APP_MODE",
            AppMode.PRODUCTION,
        ),
    ):
        logger._configure_root_logger()

    console_cls.assert_not_called()

    root_logger.addHandler.assert_called_once_with(file_handler)


def test_get_logger():
    app_logger = MagicMock()

    with (
        patch(
            "app.utils.logger._configure_root_logger",
        ) as configure,
        patch(
            "app.utils.logger.logging.getLogger",
            return_value=app_logger,
        ) as get_logger,
    ):
        result = logger.get_logger("my_logger")

    configure.assert_called_once()

    get_logger.assert_called_once_with("my_logger")

    assert result is app_logger