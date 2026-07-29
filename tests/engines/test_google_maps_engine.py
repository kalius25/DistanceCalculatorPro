from unittest.mock import MagicMock

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)

from app.configuration.models import GoogleMapsConfig
from app.engines.google_maps_engine import GoogleMapsEngine
from app.enums.travel_mode import TravelMode
from app.exceptions import (
    EngineException,
    ErrorCode,
    ParserException,
)
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest


@pytest.fixture
def engine_config() -> GoogleMapsConfig:
    return GoogleMapsConfig(
        base_url=(
            "https://www.google.com/maps/dir/?api=1"
        ),
        action_timeout=30_000,
    )


@pytest.fixture
def locator():
    return MagicMock()


@pytest.fixture
def parser():
    return MagicMock()


@pytest.fixture
def engine(
    engine_config,
    locator,
    parser,
):
    return GoogleMapsEngine(
        config=engine_config,
        locator=locator,
        parser=parser,
    )


def make_request():
    return RouteRequest(
        origin="Can Tho",
        destination="Ho Chi Minh",
        travel_mode=TravelMode.DRIVING,
        timeout=30,
    )


def make_route():
    return RouteOption(
        summary="Fastest",
        distance_text="10 km",
        duration_text="15 phút",
        distance_km=10,
        duration_minutes=15,
    )


def test_constructor_stores_dependencies(
    engine_config,
    locator,
    parser,
):
    engine = GoogleMapsEngine(
        config=engine_config,
        locator=locator,
        parser=parser,
    )

    assert engine._config is engine_config
    assert engine._locator is locator
    assert engine._parser is parser


def test_validate_empty_origin():
    request = make_request()
    request.origin = ""

    with pytest.raises(
        ValueError,
        match="Origin",
    ):
        GoogleMapsEngine._validate_request(request)


def test_validate_empty_destination():
    request = make_request()
    request.destination = ""

    with pytest.raises(
        ValueError,
        match="Destination",
    ):
        GoogleMapsEngine._validate_request(request)


@pytest.mark.parametrize(
    "timeout",
    [
        0,
        -1,
        -100,
    ],
)
def test_validate_timeout(timeout):
    request = make_request()
    request.timeout = timeout

    with pytest.raises(
        ValueError,
        match="Timeout",
    ):
        GoogleMapsEngine._validate_request(request)


def test_validate_success():
    GoogleMapsEngine._validate_request(
        make_request()
    )


def test_select_travel_mode_invalid(
    engine,
):
    request = make_request()
    request.travel_mode = MagicMock()

    with pytest.raises(
        NotImplementedError,
        match="Unsupported travel mode",
    ):
        engine._select_travel_mode(
            MagicMock(),
            request,
        )


def test_select_travel_mode_driving(
    engine,
):
    page = MagicMock()
    locator = MagicMock()

    engine._travel_mode_locators = {
        TravelMode.DRIVING: lambda _: locator,
    }

    engine._select_travel_mode(
        page,
        make_request(),
    )

    locator.click.assert_called_once_with(
        timeout=30_000,
    )


def test_fill_route_input(
    engine,
    locator,
):
    page = MagicMock()
    route_input = MagicMock()

    locator.route_input.return_value = route_input

    engine._fill_route_input(
        page,
        index=0,
        value="Can Tho",
    )

    locator.route_input.assert_called_once_with(
        page,
        0,
    )

    route_input.wait_for.assert_called_once_with(
        state="visible",
        timeout=30_000,
    )

    route_input.fill.assert_called_once_with(
        "Can Tho"
    )


def test_find_routes(
    engine,
    locator,
    parser,
):
    page = MagicMock()
    route_panel = MagicMock()
    parser_result = [make_route()]

    locator.route_panel.return_value = route_panel
    parser.parse.return_value = parser_result

    engine._fill_route_input = MagicMock()
    engine._select_travel_mode = MagicMock()

    request = make_request()

    result = engine.find_routes(
        page,
        request,
    )

    page.goto.assert_called_once_with(
        "https://www.google.com/maps/dir/?api=1",
        timeout=30_000,
    )

    assert engine._fill_route_input.call_count == 2

    engine._fill_route_input.assert_any_call(
        page=page,
        index=0,
        value="Can Tho",
    )

    engine._fill_route_input.assert_any_call(
        page=page,
        index=1,
        value="Ho Chi Minh",
    )

    engine._select_travel_mode.assert_called_once_with(
        page=page,
        request=request,
    )

    locator.route_panel.assert_called_once_with(
        page
    )

    route_panel.wait_for.assert_called_once_with(
        state="visible",
        timeout=30_000,
    )

    parser.parse.assert_called_once_with(page)

    assert result == parser_result


def test_find_routes_timeout_raises_engine_exception(
    engine,
):
    page = MagicMock()
    request = make_request()

    page.goto.side_effect = PlaywrightTimeoutError(
        "Navigation timeout"
    )

    with pytest.raises(
        EngineException,
    ) as exc_info:
        engine.find_routes(
            page,
            request,
        )

    exception = exc_info.value

    assert (
        exception.error_code
        is ErrorCode.ENGINE_ERROR
    )

    assert isinstance(
        exception.cause,
        PlaywrightTimeoutError,
    )

    assert exception.context == {
        "origin": request.origin,
        "destination": request.destination,
        "travel_mode": request.travel_mode.value,
        "timeout": request.timeout,
    }


def test_find_routes_playwright_error(
    engine,
):
    page = MagicMock()
    request = make_request()

    page.goto.side_effect = PlaywrightError(
        "Browser crashed"
    )

    with pytest.raises(
        EngineException,
    ) as exc_info:
        engine.find_routes(
            page,
            request,
        )

    exception = exc_info.value

    assert (
        exception.error_code
        is ErrorCode.ENGINE_ERROR
    )

    assert isinstance(
        exception.cause,
        PlaywrightError,
    )

    assert exception.context == {
        "origin": request.origin,
        "destination": request.destination,
        "travel_mode": request.travel_mode.value,
        "timeout": request.timeout,
    }


def test_find_routes_reraises_parser_exception(
    engine,
    locator,
    parser,
):
    page = MagicMock()
    route_panel = MagicMock()

    locator.route_panel.return_value = route_panel

    parser.parse.side_effect = ParserException(
        "Parse failed"
    )

    engine._fill_route_input = MagicMock()
    engine._select_travel_mode = MagicMock()

    with pytest.raises(
        ParserException,
        match="Parse failed",
    ):
        engine.find_routes(
            page,
            make_request(),
        )