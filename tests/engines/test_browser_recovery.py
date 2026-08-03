from unittest.mock import MagicMock

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.engines.browser_recovery import BrowserRecoveryManager
from app.engines.recovery_models import RecoveryAction
from app.exceptions import EngineException


def test_prepare_keeps_healthy_browser() -> None:
    browser = MagicMock()
    browser.is_healthy = True
    recovery = BrowserRecoveryManager(browser)

    recovery.prepare()

    browser.restart.assert_not_called()
    assert recovery.metrics.browser_restarts == 0


def test_prepare_restarts_unhealthy_browser() -> None:
    browser = MagicMock()
    browser.is_healthy = False
    recovery = BrowserRecoveryManager(browser)

    recovery.prepare()

    browser.restart.assert_called_once_with()
    assert recovery.metrics.browser_restarts == 1


def test_recover_timeout_replaces_page_without_browser_restart() -> None:
    browser = MagicMock()
    recovery = BrowserRecoveryManager(browser)

    action = recovery.recover(PlaywrightTimeoutError("timed out"))

    assert action is RecoveryAction.REPLACE_PAGE
    assert recovery.metrics.page_failures == 1
    assert recovery.metrics.navigation_timeouts == 1
    browser.restart.assert_not_called()


def test_recover_target_closed_restarts_browser() -> None:
    browser = MagicMock()
    recovery = BrowserRecoveryManager(browser)

    action = recovery.recover(PlaywrightError("Target page has been closed"))

    assert action is RecoveryAction.RESTART_BROWSER
    browser.restart.assert_called_once_with()
    assert recovery.metrics.page_failures == 1
    assert recovery.metrics.browser_restarts == 1


def test_classify_engine_exception_uses_underlying_cause() -> None:
    error = EngineException(
        "Google Maps request timed out.",
        cause=PlaywrightTimeoutError("navigation timeout"),
    )

    assert BrowserRecoveryManager.classify(error) is RecoveryAction.REPLACE_PAGE


def test_classify_non_browser_error_returns_none() -> None:
    action = BrowserRecoveryManager.classify(ValueError("bad input"))

    assert action is RecoveryAction.NONE


def test_restart_failure_is_recorded_and_reraised() -> None:
    browser = MagicMock()
    browser.is_healthy = False
    browser.restart.side_effect = RuntimeError("restart failed")
    recovery = BrowserRecoveryManager(browser)

    with pytest.raises(RuntimeError, match="restart failed"):
        recovery.prepare()

    assert recovery.metrics.recovery_failures == 1


def test_recover_non_browser_error_returns_none_without_recovery() -> None:
    browser = MagicMock()
    diagnostics = MagicMock()
    recovery = BrowserRecoveryManager(
        browser,
        diagnostics=diagnostics,
    )

    action = recovery.recover(
        ValueError("invalid route input"),
    )

    assert action is RecoveryAction.NONE

    browser.restart.assert_not_called()

    assert recovery.metrics.page_failures == 0
    assert recovery.metrics.navigation_timeouts == 0
    assert recovery.metrics.browser_restarts == 0
    assert recovery.metrics.recovery_failures == 0

    diagnostics.trace_browser.assert_called_once()


def test_recover_generic_playwright_error_restarts_browser() -> None:
    browser = MagicMock()
    recovery = BrowserRecoveryManager(browser)

    action = recovery.recover(
        PlaywrightError(
            "Playwright protocol operation failed",
        )
    )

    assert action is RecoveryAction.RESTART_BROWSER

    browser.restart.assert_called_once_with()

    assert recovery.metrics.page_failures == 1
    assert recovery.metrics.browser_restarts == 1
    assert recovery.metrics.navigation_timeouts == 0
