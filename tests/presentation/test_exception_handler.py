import logging
import sys
from unittest.mock import MagicMock, patch

from app.presentation.exception_handler import ExceptionHandler


def test_install_and_restore_exception_hook() -> None:
    logger = MagicMock(spec=logging.Logger)
    previous_hook = sys.excepthook
    handler = ExceptionHandler(logger)

    try:
        handler.install()
        assert sys.excepthook == handler.handle
    finally:
        handler.restore()

    assert sys.excepthook is previous_hook


def test_keyboard_interrupt_is_delegated_to_previous_hook() -> None:
    logger = MagicMock(spec=logging.Logger)
    previous_hook = MagicMock()

    with patch("app.presentation.exception_handler.sys.excepthook", previous_hook):
        handler = ExceptionHandler(logger)

    exception = KeyboardInterrupt()
    handler.handle(KeyboardInterrupt, exception, None)

    previous_hook.assert_called_once_with(KeyboardInterrupt, exception, None)
    logger.critical.assert_not_called()


def test_regular_exception_is_logged_and_shown() -> None:
    logger = MagicMock(spec=logging.Logger)
    handler = ExceptionHandler(logger)
    exception = RuntimeError("failure")

    with patch(
        "app.presentation.exception_handler.QMessageBox.critical"
    ) as critical_message:
        handler.handle(RuntimeError, exception, None)

    logger.critical.assert_called_once_with(
        "Unhandled presentation exception",
        exc_info=(RuntimeError, exception, None),
    )
    critical_message.assert_called_once_with(
        None,
        "Unexpected Error",
        (
            "DistanceCalculatorPro encountered an unexpected error. "
            "Details were written to the application log."
        ),
    )
