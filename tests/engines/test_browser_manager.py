from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from app.configuration.models import BrowserConfig
from app.engines.browser_manager import BrowserManager
from app.exceptions.engine_exception import EngineException


@pytest.fixture
def browser_config() -> BrowserConfig:
    return BrowserConfig(
        headless=True,
        timeout=30_000,
        slow_mo=50,
        viewport_width=1920,
        viewport_height=1080,
        user_agent=None,
        locale="vi-VN",
    )


def test_constructor(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    assert manager._config is browser_config
    assert manager._playwright is None
    assert manager._browser is None
    assert manager._context is None


def test_start(
    browser_config: BrowserConfig,
):
    playwright = MagicMock()
    browser = MagicMock()
    context = MagicMock()
    starter = MagicMock()

    starter.start.return_value = playwright
    playwright.chromium.launch.return_value = browser
    browser.new_context.return_value = context

    with (
        patch(
            "app.engines.browser_manager.sync_playwright",
            return_value=starter,
        ),
        patch(
            "app.engines.browser_manager.resolve_browser_executable",
            return_value=Path("bundled/chrome.exe"),
        ),
    ):
        manager = BrowserManager(browser_config)
        manager.start()

    starter.start.assert_called_once_with()

    playwright.chromium.launch.assert_called_once_with(
        executable_path=str(Path("bundled/chrome.exe")),
        headless=True,
        slow_mo=50,
    )

    browser.new_context.assert_called_once_with(
        locale="vi-VN",
        viewport={
            "width": 1920,
            "height": 1080,
        },
    )

    context.set_default_timeout.assert_called_once_with(
        30_000,
    )

    assert manager._playwright is playwright
    assert manager._browser is browser
    assert manager._context is context


def test_start_with_custom_user_agent():
    config = BrowserConfig(
        headless=False,
        timeout=15_000,
        slow_mo=0,
        viewport_width=1280,
        viewport_height=720,
        user_agent="DistanceCalculatorPro/1.0",
        locale="en-US",
    )

    playwright = MagicMock()
    browser = MagicMock()
    context = MagicMock()
    starter = MagicMock()

    starter.start.return_value = playwright
    playwright.chromium.launch.return_value = browser
    browser.new_context.return_value = context

    with (
        patch(
            "app.engines.browser_manager.sync_playwright",
            return_value=starter,
        ),
        patch(
            "app.engines.browser_manager.resolve_browser_executable",
            return_value=Path("bundled/chrome.exe"),
        ),
    ):
        manager = BrowserManager(config)
        manager.start()

    playwright.chromium.launch.assert_called_once_with(
        executable_path=str(Path("bundled/chrome.exe")),
        headless=False,
        slow_mo=0,
    )

    browser.new_context.assert_called_once_with(
        locale="en-US",
        viewport={
            "width": 1280,
            "height": 720,
        },
        user_agent="DistanceCalculatorPro/1.0",
    )

    context.set_default_timeout.assert_called_once_with(
        15_000,
    )


def test_start_only_once(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    existing_browser = MagicMock()
    manager._browser = existing_browser

    with patch(
        "app.engines.browser_manager.sync_playwright",
    ) as sync_playwright_mock:
        manager.start()

    sync_playwright_mock.assert_not_called()
    assert manager._browser is existing_browser


def test_new_page(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    page = MagicMock()
    context = MagicMock()
    context.new_page.return_value = page

    manager._context = context

    result = manager.new_page()

    assert result is page
    context.new_page.assert_called_once_with()


def test_new_page_raises_when_not_started(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    with pytest.raises(
        EngineException,
        match="Browser chưa được khởi động.",
    ):
        manager.new_page()


def test_close(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    context = MagicMock()
    browser = MagicMock()
    playwright = MagicMock()

    manager._context = context
    manager._browser = browser
    manager._playwright = playwright

    manager.close()

    context.close.assert_called_once_with()
    browser.close.assert_called_once_with()
    playwright.stop.assert_called_once_with()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_close_without_context(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    browser = MagicMock()
    playwright = MagicMock()

    manager._browser = browser
    manager._playwright = playwright

    manager.close()

    browser.close.assert_called_once_with()
    playwright.stop.assert_called_once_with()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_close_without_browser(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    context = MagicMock()
    playwright = MagicMock()

    manager._context = context
    manager._playwright = playwright

    manager.close()

    context.close.assert_called_once_with()
    playwright.stop.assert_called_once_with()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_close_without_playwright(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    context = MagicMock()
    browser = MagicMock()

    manager._context = context
    manager._browser = browser

    manager.close()

    context.close.assert_called_once_with()
    browser.close.assert_called_once_with()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_close_when_already_closed(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    manager.close()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_close_can_be_called_repeatedly(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    context = MagicMock()
    browser = MagicMock()
    playwright = MagicMock()

    manager._context = context
    manager._browser = browser
    manager._playwright = playwright

    manager.close()
    manager.close()

    context.close.assert_called_once_with()
    browser.close.assert_called_once_with()
    playwright.stop.assert_called_once_with()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_enter_starts_manager(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    with patch.object(
        manager,
        "start",
    ) as start_mock:
        returned_manager = manager.__enter__()

    start_mock.assert_called_once_with()
    assert returned_manager is manager


def test_exit_closes_manager(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    with patch.object(
        manager,
        "close",
    ) as close_mock:
        result = manager.__exit__(
            None,
            None,
            None,
        )

    close_mock.assert_called_once_with()
    assert result is None


def test_exit_closes_manager_when_exception_occurs(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    error = RuntimeError("Test error")

    with patch.object(
        manager,
        "close",
    ) as close_mock:
        result = manager.__exit__(
            RuntimeError,
            error,
            None,
        )

    close_mock.assert_called_once_with()
    assert result is None


def test_context_manager_starts_and_closes(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    with (
        patch.object(
            manager,
            "start",
        ) as start_mock,
        patch.object(
            manager,
            "close",
        ) as close_mock,
    ):
        with manager as returned_manager:
            assert returned_manager is manager

    start_mock.assert_called_once_with()
    close_mock.assert_called_once_with()


def test_context_manager_closes_when_body_raises(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    with (
        patch.object(
            manager,
            "start",
        ) as start_mock,
        patch.object(
            manager,
            "close",
        ) as close_mock,
        pytest.raises(
            RuntimeError,
            match="Body failure",
        ),
    ):
        with manager:
            raise RuntimeError("Body failure")

    start_mock.assert_called_once_with()
    close_mock.assert_called_once_with()


def test_start_reuses_existing_managed_state(
    browser_config: BrowserConfig,
):
    manager = BrowserManager(browser_config)

    existing_playwright = MagicMock()
    existing_browser = MagicMock()
    existing_context = MagicMock()

    manager._playwright = existing_playwright
    manager._browser = existing_browser
    manager._context = existing_context

    with patch(
        "app.engines.browser_manager.sync_playwright",
    ) as sync_playwright_mock:
        manager.start()

    sync_playwright_mock.assert_not_called()

    assert manager._playwright is existing_playwright
    assert manager._browser is existing_browser
    assert manager._context is existing_context


def test_health_properties_and_restart(
    browser_config: BrowserConfig,
) -> None:
    manager = BrowserManager(browser_config)

    assert not manager.is_started
    assert not manager.is_healthy

    browser = MagicMock()
    browser.is_connected.return_value = True
    manager._browser = browser
    manager._context = MagicMock()

    assert manager.is_started
    assert manager.is_healthy

    with (
        patch.object(manager, "close") as close_mock,
        patch.object(manager, "start") as start_mock,
    ):
        manager.restart()

    close_mock.assert_called_once_with()
    start_mock.assert_called_once_with()


def test_health_returns_false_when_playwright_check_fails(
    browser_config: BrowserConfig,
) -> None:
    manager = BrowserManager(browser_config)
    browser = MagicMock()
    browser.is_connected.side_effect = __import__(
        "playwright.sync_api", fromlist=["Error"]
    ).Error("disconnected")
    manager._browser = browser
    manager._context = MagicMock()

    assert not manager.is_healthy


def test_close_ignores_playwright_cleanup_errors(
    browser_config: BrowserConfig,
) -> None:
    error_type = __import__("playwright.sync_api", fromlist=["Error"]).Error
    manager = BrowserManager(browser_config)
    manager._context = MagicMock()
    manager._context.close.side_effect = error_type("context closed")
    manager._browser = MagicMock()
    manager._browser.close.side_effect = error_type("browser closed")
    manager._playwright = MagicMock()
    manager._playwright.stop.side_effect = error_type("playwright stopped")

    manager.close()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_start_resolves_executable_before_starting_playwright(
    browser_config: BrowserConfig,
) -> None:
    calls: list[str] = []
    playwright = MagicMock()
    browser = MagicMock()
    context = MagicMock()
    starter = MagicMock()
    starter.start.return_value = playwright
    playwright.chromium.launch.return_value = browser
    browser.new_context.return_value = context

    def resolve() -> Path:
        calls.append("resolve")
        return Path("bundled/chrome.exe")

    def create_playwright() -> MagicMock:
        calls.append("sync")
        return starter

    with (
        patch(
            "app.engines.browser_manager.resolve_browser_executable",
            side_effect=resolve,
        ),
        patch(
            "app.engines.browser_manager.sync_playwright",
            side_effect=create_playwright,
        ),
    ):
        BrowserManager(browser_config).start()

    assert calls == ["resolve", "sync"]
