from unittest.mock import MagicMock


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
    engine.find_routes.side_effect = RuntimeError("Google timeout")

    provider = GoogleWebProvider(
        browser=browser,
        engine=engine,
    )

    result = provider.calculate(request)

    assert result.success is False
    assert result.provider == "google_web"
    assert result.error == "Google timeout"


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

from unittest.mock import MagicMock
from unittest.mock import patch

from app.providers.google_web_provider import GoogleWebProvider

def test_constructor_creates_default_engine():
    browser = MagicMock()

    fake_engine = MagicMock()

    with patch(
        "app.engines.google_maps_engine.GoogleMapsEngine",
        return_value=fake_engine,
    ) as engine_cls:
        provider = GoogleWebProvider(
            browser=browser,
            engine=None,
        )

    engine_cls.assert_called_once_with()
    assert provider._engine is fake_engine
    assert provider._browser is browser