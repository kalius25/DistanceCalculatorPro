from unittest.mock import MagicMock
from unittest.mock import patch

from app.models.route_option import RouteOption
from app.parsers.google_maps_parser import GoogleMapsParser
from app.parsers.google_maps_parser import _parse_locator
from app.parsers.google_maps_parser import _parse_text
from app.parsers.google_maps_parser import _extract_summary
from app.utils.text_converter import TextConverter


def make_option(summary: str = "QL1A") -> RouteOption:
    return RouteOption(
        summary=summary,
        distance_text="10 km",
        distance_km=10.0,
        duration_text="20 phút",
        duration_minutes=20,
        has_toll=False,
        has_ferry=False,
        has_highway=False,
        raw={},
    )


def make_locator(count: int) -> MagicMock:
    locator = MagicMock()
    locator.count.return_value = count
    return locator


def test_parse_returns_empty_when_no_route_cards():
    page = MagicMock()
    locator = make_locator(0)

    with patch(
        "app.parsers.google_maps_parser.GoogleMapsLocator.route_cards",
        return_value=locator,
    ):
        routes = GoogleMapsParser.parse(page)

    assert routes == []


def test_parse_returns_single_route():
    page = MagicMock()
    locator = make_locator(1)

    with (
        patch(
            "app.parsers.google_maps_parser.GoogleMapsLocator.route_cards",
            return_value=locator,
        ),
        patch(
            "app.parsers.google_maps_parser._parse_locator",
            return_value=make_option(),
        ),
    ):
        routes = GoogleMapsParser.parse(page)

    assert len(routes) == 1
    assert routes[0].summary == "QL1A"


def test_parse_returns_multiple_routes():
    page = MagicMock()
    locator = make_locator(2)

    with (
        patch(
            "app.parsers.google_maps_parser.GoogleMapsLocator.route_cards",
            return_value=locator,
        ),
        patch(
            "app.parsers.google_maps_parser._parse_locator",
            side_effect=[
                make_option("QL1A"),
                make_option("CT01"),
            ],
        ),
    ):
        routes = GoogleMapsParser.parse(page)

    assert len(routes) == 2
    assert routes[0].summary == "QL1A"
    assert routes[1].summary == "CT01"


def test_parse_skips_invalid_route():
    page = MagicMock()
    locator = make_locator(2)

    with (
        patch(
            "app.parsers.google_maps_parser.GoogleMapsLocator.route_cards",
            return_value=locator,
        ),
        patch(
            "app.parsers.google_maps_parser._parse_locator",
            side_effect=[
                None,
                make_option("QL1A"),
            ],
        ),
    ):
        routes = GoogleMapsParser.parse(page)

    assert len(routes) == 1
    assert routes[0].summary == "QL1A"


def test_parse_respects_parser_max_routes():
    page = MagicMock()
    locator = make_locator(999)

    with (
        patch(
            "app.parsers.google_maps_parser.GoogleMapsLocator.route_cards",
            return_value=locator,
        ),
        patch(
            "app.parsers.google_maps_parser.config.PARSER_MAX_ROUTES",
            3,
        ),
        patch(
            "app.parsers.google_maps_parser._parse_locator",
            side_effect=[
                make_option("A"),
                make_option("B"),
                make_option("C"),
            ],
        ) as parser,
    ):
        routes = GoogleMapsParser.parse(page)

    assert len(routes) == 3
    assert parser.call_count == 3
    assert locator.nth.call_count == 3

def test_parse_locator():
    card = MagicMock()
    card.inner_text.return_value = """
QL1A
10 km
20 phút
"""

    option = _parse_locator(card)

    assert option is not None

def test_parse_text_returns_none_when_distance_conversion_fails(monkeypatch):
    monkeypatch.setattr(
        TextConverter,
        "distance_to_km",
        lambda _: None,
    )

    text = """
QL1A
10 km
20 phút
"""

    assert _parse_text(text) is None

def test_parse_text_returns_none_when_duration_conversion_fails(monkeypatch):
    monkeypatch.setattr(
        TextConverter,
        "duration_to_minutes",
        lambda _: None,
    )

    text = """
QL1A
10 km
20 phút
"""

    assert _parse_text(text) is None

def test_extract_summary_skips_single_character():
    text = """
A
10 km
20 phút
"""

    assert _extract_summary(text) == ""