from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from app.engines.browser_manager import BrowserManager
from app.exceptions.engine_exception import EngineException


def test_constructor():
    manager = BrowserManager(headless=False)

    assert manager._headless is False
    assert manager._playwright is None
    assert manager._browser is None
    assert manager._context is None


def test_start():
    playwright = MagicMock()
    browser = MagicMock()
    context = MagicMock()

    playwright.chromium.launch.return_value = browser
    browser.new_context.return_value = context

    starter = MagicMock()
    starter.start.return_value = playwright

    with patch(
        "app.engines.browser_manager.sync_playwright",
        return_value=starter,
    ):
        manager = BrowserManager(headless=True)
        manager.start()

    starter.start.assert_called_once()
    playwright.chromium.launch.assert_called_once_with(headless=True)
    browser.new_context.assert_called_once()

    assert manager._playwright is playwright
    assert manager._browser is browser
    assert manager._context is context


def test_start_only_once():
    manager = BrowserManager()

    manager._browser = MagicMock()

    with patch(
        "app.engines.browser_manager.sync_playwright",
    ) as playwright:
        manager.start()

    playwright.assert_not_called()


def test_new_page():
    manager = BrowserManager()

    page = MagicMock()

    manager._context = MagicMock()
    manager._context.new_page.return_value = page

    assert manager.new_page() is page


def test_new_page_raise_exception():
    manager = BrowserManager()

    with pytest.raises(
        EngineException,
        match="Browser chưa được khởi động.",
    ):
        manager.new_page()


def test_close():
    manager = BrowserManager()

    manager._context = MagicMock()
    manager._browser = MagicMock()
    manager._playwright = MagicMock()

    manager.close()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_enter():
    manager = BrowserManager()

    with patch.object(manager, "start") as start:
        returned = manager.__enter__()

    start.assert_called_once()
    assert returned is manager


def test_exit():
    manager = BrowserManager()

    with patch.object(manager, "close") as close:
        manager.__exit__(None, None, None)

    close.assert_called_once()

def test_close_without_context():
    manager = BrowserManager()

    manager._browser = MagicMock()
    manager._playwright = MagicMock()

    manager.close()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_close_without_browser():
    manager = BrowserManager()

    manager._context = MagicMock()
    manager._playwright = MagicMock()

    manager.close()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None


def test_close_without_playwright():
    manager = BrowserManager()

    manager._context = MagicMock()
    manager._browser = MagicMock()

    manager.close()

    assert manager._context is None
    assert manager._browser is None
    assert manager._playwright is None