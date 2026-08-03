from unittest.mock import MagicMock, patch

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.configuration.models import GoogleMapsConfig
from app.engines.google_maps_engine import GoogleMapsEngine
from app.engines.google_maps_url_builder import GoogleMapsUrlBuilder
from app.enums.travel_mode import TravelMode
from app.exceptions import EngineException, ErrorCode, ParserException
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest


@pytest.fixture
def engine_config() -> GoogleMapsConfig:
    return GoogleMapsConfig(
        base_url="https://www.google.com/maps/dir/",
        action_timeout=30_000,
    )


@pytest.fixture
def locator():
    return MagicMock()


@pytest.fixture
def parser():
    return MagicMock()


@pytest.fixture
def engine(engine_config, locator, parser):
    return GoogleMapsEngine(engine_config, locator, parser)


def make_request() -> RouteRequest:
    return RouteRequest(
        origin="Can Tho",
        destination="Ho Chi Minh",
        travel_mode=TravelMode.DRIVING,
        timeout=30,
    )


def make_route() -> RouteOption:
    return RouteOption(
        summary="Fastest",
        distance_text="10 km",
        duration_text="15 phút",
        distance_km=10,
        duration_minutes=15,
    )


def test_constructor_stores_dependencies(engine_config, locator, parser):
    engine = GoogleMapsEngine(engine_config, locator, parser)
    assert engine._config is engine_config
    assert engine._locator is locator
    assert engine._parser is parser


def test_validate_request():
    request = make_request()
    request.origin = ""
    with pytest.raises(ValueError, match="Origin"):
        GoogleMapsEngine._validate_request(request)

    request = make_request()
    request.destination = ""
    with pytest.raises(ValueError, match="Destination"):
        GoogleMapsEngine._validate_request(request)

    for timeout in (0, -1, -100):
        request = make_request()
        request.timeout = timeout
        with pytest.raises(ValueError, match="Timeout"):
            GoogleMapsEngine._validate_request(request)

    GoogleMapsEngine._validate_request(make_request())


def test_travel_mode_handling(engine):
    engine._select_non_default_travel_mode(MagicMock(), make_request())

    request = make_request()
    request.travel_mode = TravelMode.WALKING
    with pytest.raises(NotImplementedError, match="Unsupported travel mode"):
        engine._select_non_default_travel_mode(MagicMock(), request)


def test_find_routes_uses_complete_url(engine, locator, parser):
    page = MagicMock()
    route_cards = MagicMock()
    locator.route_cards.return_value = route_cards
    parser_result = [make_route()]
    parser.parse.return_value = parser_result
    request = make_request()

    result = engine.find_routes(page, request)

    expected_url = GoogleMapsUrlBuilder.build(request)
    page.goto.assert_called_once_with(
        expected_url,
        timeout=30_000,
        wait_until="domcontentloaded",
    )
    locator.route_cards.assert_called_once_with(page)
    route_cards.first.wait_for.assert_called_once_with(
        state="visible",
        timeout=30_000,
    )
    parser.parse.assert_called_once_with(page, engine._diagnostics)
    assert result == parser_result


def test_find_routes_timeout_raises_engine_exception(engine):
    page = MagicMock()
    page.goto.side_effect = PlaywrightTimeoutError("Navigation timeout")
    request = make_request()

    with pytest.raises(EngineException) as exc_info:
        engine.find_routes(page, request)

    exception = exc_info.value
    assert exception.error_code is ErrorCode.ENGINE_ERROR
    assert isinstance(exception.cause, PlaywrightTimeoutError)
    assert exception.context["origin"] == request.origin
    assert exception.context["url"].startswith("https://www.google.com/maps/dir/")


def test_find_routes_playwright_error(engine):
    page = MagicMock()
    page.goto.side_effect = PlaywrightError("Browser crashed")

    with pytest.raises(EngineException) as exc_info:
        engine.find_routes(page, make_request())

    assert exc_info.value.error_code is ErrorCode.ENGINE_ERROR
    assert isinstance(exc_info.value.cause, PlaywrightError)
    assert "url" in exc_info.value.context


def test_find_routes_reraises_parser_exception(engine, locator, parser):
    page = MagicMock()
    locator.route_cards.return_value = MagicMock()
    parser.parse.side_effect = ParserException("Parse failed")

    with pytest.raises(ParserException, match="Parse failed"):
        engine.find_routes(page, make_request())


def test_capture_failure_skips_closed_page(engine):
    page = MagicMock()
    page.is_closed.return_value = True

    with patch.object(engine._diagnostics, "capture_page") as capture_page:
        engine._capture_failure(page, "https://example.test", "closed")

    capture_page.assert_not_called()


def test_capture_failure_ignores_playwright_cleanup_error(engine):
    page = MagicMock()
    page.is_closed.side_effect = PlaywrightError("closed")

    with patch.object(engine._diagnostics, "capture_page") as capture_page:
        engine._capture_failure(page, "https://example.test", "error")

    capture_page.assert_not_called()


def test_capture_failure_captures_open_page(engine):
    page = MagicMock()
    page.is_closed.return_value = False

    with patch.object(engine._diagnostics, "capture_page") as capture_page:
        engine._capture_failure(page, "https://example.test", "timeout")

    capture_page.assert_called_once_with(
        page,
        label="timeout",
        payload={
            "url": "https://example.test",
            "failure": "timeout",
        },
    )
