from unittest.mock import MagicMock, patch

import pytest

from app.exceptions import EngineException, ErrorCode
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.providers.google_web_provider import GoogleWebProvider


def make_request() -> RouteRequest:
    return RouteRequest(
        origin="A",
        destination="B",
    )


def make_route() -> RouteOption:
    return RouteOption(
        summary="Fastest",
        distance_text="10 km",
        duration_text="15 phút",
        distance_km=10,
        duration_minutes=15,
    )


def make_browser():
    browser = MagicMock()

    context = MagicMock()
    context.new_page.return_value = MagicMock()

    browser.__enter__.return_value = context
    browser.__exit__.return_value = False

    return browser, context


def make_engine(routes=None):
    engine = MagicMock()

    if routes is None:
        routes = [make_route()]

    engine.find_routes.return_value = routes

    return engine


def test_calculate_success():
    request = make_request()

    browser, context = make_browser()
    engine = make_engine()

    provider = GoogleWebProvider(
        browser=browser,
        engine=engine,
    )

    result = provider.calculate(request)

    assert result.success is True
    assert result.request == request
    assert result.provider == "google_web"
    assert len(result.routes) == 1


def test_new_page_called():
    request = make_request()

    browser, context = make_browser()
    engine = make_engine()

    provider = GoogleWebProvider(
        browser=browser,
        engine=engine,
    )

    provider.calculate(request)

    context.new_page.assert_called_once()


def test_engine_called():
    request = make_request()

    browser, context = make_browser()
    engine = make_engine()

    provider = GoogleWebProvider(
        browser=browser,
        engine=engine,
    )

    provider.calculate(request)

    engine.find_routes.assert_called_once_with(
        context.new_page.return_value,
        request,
    )


def test_calculate_exception():
    request = make_request()

    browser, context = make_browser()

    engine = MagicMock()

    engine.find_routes.side_effect = EngineException(
        "Google timeout",
        cause=TimeoutError("Navigation timeout"),
        context={
            "timeout": 30,
            "provider": "google_web",
        },
    )

    provider = GoogleWebProvider(
        browser=browser,
        engine=engine,
    )

    result = provider.calculate(request)

    assert result.success is False

    assert result.provider == "google_web"

    assert result.error == "Google timeout"

    assert result.error_code is ErrorCode.ENGINE_ERROR

    assert result.context == {
        "timeout": 30,
        "provider": "google_web",
    }

    engine.find_routes.assert_called_once()

def test_browser_context_closed():
    request = make_request()

    browser, context = make_browser()
    engine = make_engine()

    provider = GoogleWebProvider(
        browser=browser,
        engine=engine,
    )

    provider.calculate(request)

    browser.__enter__.assert_called_once()
    browser.__exit__.assert_called_once()

def test_calculate_unexpected_exception():
    request = make_request()

    browser, context = make_browser()

    engine = MagicMock()

    engine.find_routes.side_effect = RuntimeError("Unexpected bug")

    provider = GoogleWebProvider(
        browser=browser,
        engine=engine,
    )

    with pytest.raises(RuntimeError, match="Unexpected bug"):
        provider.calculate(request)

def test_constructor_stores_injected_dependencies():
    browser = MagicMock()
    engine = MagicMock()

    provider = GoogleWebProvider(
        browser=browser,
        engine=engine,
    )

    assert provider._browser is browser
    assert provider._engine is engine

def test_constructor_does_not_create_default_dependencies():
    browser = MagicMock()
    engine = MagicMock()

    with (
        patch(
            "app.providers.google_web_provider.BrowserManager",
        ) as browser_class,
        patch(
            "app.providers.google_web_provider.GoogleMapsEngine",
        ) as engine_class,
    ):
        provider = GoogleWebProvider(
            browser=browser,
            engine=engine,
        )

    browser_class.assert_not_called()
    engine_class.assert_not_called()

    assert provider._browser is browser
    assert provider._engine is engine