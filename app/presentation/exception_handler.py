from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from types import TracebackType
from typing import Any

from PySide6.QtWidgets import QMessageBox

ExceptionHook = Callable[
    [type[BaseException], BaseException, TracebackType | None],
    Any,
]


class ExceptionHandler:
    """Routes unhandled exceptions to technical logs and a safe UI message."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._previous_hook: ExceptionHook = sys.excepthook

    def install(self) -> None:
        sys.excepthook = self.handle

    def restore(self) -> None:
        sys.excepthook = self._previous_hook

    def handle(
        self,
        exception_type: type[BaseException],
        exception: BaseException,
        traceback: TracebackType | None,
    ) -> None:
        if issubclass(exception_type, KeyboardInterrupt):
            self._previous_hook(exception_type, exception, traceback)
            return

        self._logger.critical(
            "Unhandled presentation exception",
            exc_info=(exception_type, exception, traceback),
        )
        QMessageBox.critical(
            None,
            "Unexpected Error",
            (
                "DistanceCalculatorPro encountered an unexpected error. "
                "Details were written to the application log."
            ),
        )
