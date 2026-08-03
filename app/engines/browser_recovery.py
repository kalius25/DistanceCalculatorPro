"""Smart recovery orchestration for Playwright browser failures."""

from __future__ import annotations

import logging

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.diagnostics import DiagnosticsManager
from app.engines.browser_manager import BrowserManager
from app.engines.recovery_models import BrowserRecoveryMetrics, RecoveryAction
from app.exceptions import EngineException


class BrowserRecoveryManager:
    """Classify failures and restore a healthy browser for the next attempt."""

    _BROWSER_FAILURE_PARTS = (
        "target page",
        "target closed",
        "browser has been closed",
        "browser closed",
        "browser disconnected",
        "context or browser has been closed",
    )
    _TIMEOUT_PARTS = ("timeout", "timed out")

    def __init__(
        self,
        browser: BrowserManager,
        diagnostics: DiagnosticsManager | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        self._browser = browser
        self._diagnostics = diagnostics or DiagnosticsManager()
        self._logger = logger or logging.getLogger(__name__)
        self.metrics = BrowserRecoveryMetrics()

    def prepare(self) -> None:
        """Ensure the shared browser is healthy before creating a page."""
        if self._browser.is_healthy:
            return
        self._restart_browser("browser_health_check_failed")

    def record_page_created(self) -> None:
        self.metrics.pages_created += 1

    def recover(self, error: BaseException) -> RecoveryAction:
        """Recover resources needed by the next retry attempt."""
        action = self.classify(error)
        self._diagnostics.trace_browser(
            self._logger,
            "RECOVERY_STARTED",
            action=action.value,
            error_type=type(error).__name__,
            error_message=str(error),
        )

        if action is RecoveryAction.NONE:
            return action
        if action is RecoveryAction.REPLACE_PAGE:
            self.metrics.page_failures += 1
            self.metrics.navigation_timeouts += 1
            self._diagnostics.trace_browser(
                self._logger,
                "PAGE_RECREATED",
            )
            return action

        self.metrics.page_failures += 1
        self._restart_browser(str(error))
        return action

    @classmethod
    def classify(cls, error: BaseException) -> RecoveryAction:
        """Map an exception to the least disruptive recovery action."""
        cause: BaseException = error
        if isinstance(error, EngineException) and error.cause is not None:
            cause = error.cause

        if isinstance(cause, PlaywrightTimeoutError):
            return RecoveryAction.REPLACE_PAGE

        message = f"{error} {cause}".casefold()
        if any(part in message for part in cls._BROWSER_FAILURE_PARTS):
            return RecoveryAction.RESTART_BROWSER
        if any(part in message for part in cls._TIMEOUT_PARTS):
            return RecoveryAction.REPLACE_PAGE
        if isinstance(cause, PlaywrightError):
            return RecoveryAction.RESTART_BROWSER
        return RecoveryAction.NONE

    def _restart_browser(self, reason: str) -> None:
        try:
            self._browser.restart()
        except Exception:
            self.metrics.recovery_failures += 1
            self._diagnostics.trace_browser(
                self._logger,
                "RECOVERY_EXHAUSTED",
                action=RecoveryAction.RESTART_BROWSER.value,
                reason=reason,
            )
            raise
        self.metrics.browser_restarts += 1
        self._diagnostics.trace_browser(
            self._logger,
            "BROWSER_RESTARTED",
            reason=reason,
            browser_restarts=self.metrics.browser_restarts,
        )
        self._diagnostics.trace_browser(
            self._logger,
            "RECOVERY_SUCCEEDED",
            action=RecoveryAction.RESTART_BROWSER.value,
        )


__all__ = ["BrowserRecoveryManager"]
