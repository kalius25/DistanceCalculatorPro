from unittest.mock import MagicMock

import pytest

from app.engines.google_maps_engine import GoogleMapsEngine
from app.enums.travel_mode import TravelMode
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest


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


def test_validate_empty_origin():
    request = make_request()
    request.origin = ""

    with pytest.raises(ValueError, match="Origin"):
        GoogleMapsEngine._validate_request(request)


def test_validate_empty_destination():
    request = make_request()
    request.destination = ""

    with pytest.raises(ValueError, match="Destination"):
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

    with pytest.raises(ValueError, match="Timeout"):
        GoogleMapsEngine._validate_request(request)


def test_validate_success():
    GoogleMapsEngine._validate_request(make_request())


def test_select_travel_mode_invalid():
    engine = GoogleMapsEngine()

    page = MagicMock()

    request = make_request()

    request.travel_mode = MagicMock()

    with pytest.raises(NotImplementedError):
        engine._select_travel_mode(
            page,
            request,
        )


def test_select_travel_mode_driving():
    engine = GoogleMapsEngine()

    page = MagicMock()

    locator = MagicMock()

    engine._TRAVEL_MODE_LOCATORS = {
        TravelMode.DRIVING: lambda _: locator,
    }

    engine._select_travel_mode(
        page,
        make_request(),
    )

    locator.click.assert_called_once()


def test_fill_route_input(monkeypatch):
    locator = MagicMock()

    from app.engines import google_maps_engine

    monkeypatch.setattr(
        google_maps_engine.GoogleMapsLocator,
        "route_input",
        lambda *_: locator,
    )

    GoogleMapsEngine._fill_route_input(
        MagicMock(),
        index=0,
        value="Can Tho",
    )

    locator.wait_for.assert_called_once()
    locator.fill.assert_called_once_with("Can Tho")


def test_find_routes(monkeypatch):
    page = MagicMock()

    route_panel = MagicMock()

    parser_result = [make_route()]

    from app.engines import google_maps_engine

    monkeypatch.setattr(
        google_maps_engine.GoogleMapsLocator,
        "route_panel",
        lambda *_: route_panel,
    )

    monkeypatch.setattr(
        google_maps_engine.GoogleMapsParser,
        "parse",
        lambda *_: parser_result,
    )

    monkeypatch.setattr(
        GoogleMapsEngine,
        "_fill_route_input",
        lambda *args, **kwargs: None,
    )

    monkeypatch.setattr(
        GoogleMapsEngine,
        "_select_travel_mode",
        lambda *args, **kwargs: None,
    )

    engine = GoogleMapsEngine()

    routes = engine.find_routes(
        page,
        make_request(),
    )

    page.goto.assert_called_once()

    route_panel.wait_for.assert_called_once()

    assert routes == parser_result
