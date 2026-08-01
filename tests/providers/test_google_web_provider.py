from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import EngineException, ErrorCode
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.providers.google_web_provider import GoogleWebProvider


def make_request() -> RouteRequest:
    return RouteRequest(origin="A", destination="B")


def make_route() -> RouteOption:
    return RouteOption(
        summary="Fastest",
        distance_text="10 km",
        duration_text="15 phút",
        distance_km=10,
        duration_minutes=15,
    )


def test_batch_lifecycle_starts_and_closes_browser_once():
    browser = MagicMock()
    engine = MagicMock()
    provider = GoogleWebProvider(browser, engine)

    provider.start_batch()
    provider.start_batch()
    assert provider._batch_started
    browser.start.assert_called_once_with()

    provider.finish_batch()
    provider.finish_batch()
    assert not provider._batch_started
    browser.close.assert_called_once_with()


def test_calculate_reuses_batch_browser_and_closes_page():
    request = make_request()
    page = MagicMock()
    page.is_closed.return_value = False
    browser = MagicMock()
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    provider.start_batch()
    result = provider.calculate(request)

    assert result.success
    browser.start.assert_called_once_with()
    browser.close.assert_not_called()
    browser.new_page.assert_called_once_with()
    engine.find_routes.assert_called_once_with(page, request)
    page.close.assert_called_once_with()

    provider.finish_batch()
    browser.close.assert_called_once_with()


def test_calculate_owns_browser_outside_batch():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    result = provider.calculate(make_request())

    assert result.success
    browser.start.assert_called_once_with()
    browser.close.assert_called_once_with()
    page.close.assert_called_once_with()


def test_calculate_engine_exception_returns_failed_result():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.side_effect = EngineException(
        "Google timeout",
        error_code=ErrorCode.ENGINE_ERROR,
        context={"timeout": 30},
    )
    provider = GoogleWebProvider(browser, engine)

    result = provider.calculate(make_request())

    assert not result.success
    assert result.provider == "google_web"
    assert result.error == "Google timeout"
    assert result.context == {"timeout": 30}
    page.close.assert_called_once_with()
    browser.close.assert_called_once_with()


def test_calculate_unexpected_exception_closes_resources():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.side_effect = RuntimeError("Unexpected bug")
    provider = GoogleWebProvider(browser, engine)

    with pytest.raises(RuntimeError, match="Unexpected bug"):
        provider.calculate(make_request())

    page.close.assert_called_once_with()
    browser.close.assert_called_once_with()


def test_calculate_closes_owned_browser_when_page_creation_fails():
    browser = MagicMock()
    browser.new_page.side_effect = RuntimeError("Page failed")
    provider = GoogleWebProvider(browser, MagicMock())

    with pytest.raises(RuntimeError, match="Page failed"):
        provider.calculate(make_request())

    browser.close.assert_called_once_with()


def test_constructor_uses_injected_dependencies_only():
    browser = MagicMock()
    engine = MagicMock()
    with (
        patch("app.providers.google_web_provider.BrowserManager") as browser_type,
        patch("app.providers.google_web_provider.GoogleMapsEngine") as engine_type,
    ):
        provider = GoogleWebProvider(browser, engine)
    browser_type.assert_not_called()
    engine_type.assert_not_called()
    assert provider._browser is browser
    assert provider._engine is engine


def test_calculate_does_not_close_already_closed_page():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = True
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    result = provider.calculate(make_request())

    assert result.success
    page.close.assert_not_called()
    browser.close.assert_called_once_with()


def test_calculate_ignores_playwright_error_while_closing_page():
    browser = MagicMock()
    page = MagicMock()
    page.is_closed.return_value = False
    page.close.side_effect = __import__(
        "playwright.sync_api", fromlist=["Error"]
    ).Error("already closed")
    browser.new_page.return_value = page
    engine = MagicMock()
    engine.find_routes.return_value = [make_route()]
    provider = GoogleWebProvider(browser, engine)

    result = provider.calculate(make_request())

    assert result.success
    browser.close.assert_called_once_with()
