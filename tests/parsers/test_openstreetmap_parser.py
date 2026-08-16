from unittest.mock import MagicMock, patch

import pytest

from app.parsers.openstreetmap_parser import (
    OpenStreetMapParser,
    _duration_to_minutes,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1:57", 117),
        ("0:45", 45),
        ("2:05", 125),
        ("1:60", None),
        ("20 min", 20),
        ("", None),
    ],
)
def test_duration_to_minutes(
    text: str,
    expected: int | None,
) -> None:
    assert _duration_to_minutes(text) == expected


def test_parse_reads_live_osm_total_outputs() -> None:
    page = MagicMock()
    distance = MagicMock()
    duration = MagicMock()
    distance.inner_text.return_value = "131 km"
    duration.inner_text.return_value = "1:57"

    with (
        patch(
            "app.parsers.openstreetmap_parser."
            "OpenStreetMapLocator.route_distance",
            return_value=distance,
        ),
        patch(
            "app.parsers.openstreetmap_parser."
            "OpenStreetMapLocator.route_duration",
            return_value=duration,
        ),
    ):
        routes = OpenStreetMapParser.parse(page)

    assert len(routes) == 1
    route = routes[0]
    assert route.distance_text == "131 km"
    assert route.distance_km == 131.0
    assert route.duration_text == "1:57"
    assert route.duration_minutes == 117
    assert route.raw["provider"] == "openstreetmap_web"


def test_parse_logs_live_osm_route() -> None:
    page = MagicMock()
    diagnostics = MagicMock()
    distance = MagicMock()
    duration = MagicMock()
    distance.inner_text.return_value = "131 km"
    duration.inner_text.return_value = "1:57"

    with (
        patch(
            "app.parsers.openstreetmap_parser."
            "OpenStreetMapLocator.route_distance",
            return_value=distance,
        ),
        patch(
            "app.parsers.openstreetmap_parser."
            "OpenStreetMapLocator.route_duration",
            return_value=duration,
        ),
    ):
        routes = OpenStreetMapParser.parse(page, diagnostics)

    diagnostics.log_routes.assert_called_once()
    assert len(routes) == 1


def test_parse_returns_empty_when_distance_is_invalid() -> None:
    page = MagicMock()
    distance = MagicMock()
    duration = MagicMock()
    distance.inner_text.return_value = "unknown"
    duration.inner_text.return_value = "1:57"

    with (
        patch(
            "app.parsers.openstreetmap_parser."
            "OpenStreetMapLocator.route_distance",
            return_value=distance,
        ),
        patch(
            "app.parsers.openstreetmap_parser."
            "OpenStreetMapLocator.route_duration",
            return_value=duration,
        ),
    ):
        assert OpenStreetMapParser.parse(page) == []


def test_parse_returns_empty_when_duration_is_invalid() -> None:
    page = MagicMock()
    distance = MagicMock()
    duration = MagicMock()
    distance.inner_text.return_value = "131 km"
    duration.inner_text.return_value = "invalid"

    with (
        patch(
            "app.parsers.openstreetmap_parser."
            "OpenStreetMapLocator.route_distance",
            return_value=distance,
        ),
        patch(
            "app.parsers.openstreetmap_parser."
            "OpenStreetMapLocator.route_duration",
            return_value=duration,
        ),
    ):
        assert OpenStreetMapParser.parse(page) == []
