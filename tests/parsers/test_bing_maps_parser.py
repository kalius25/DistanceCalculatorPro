from unittest.mock import MagicMock, patch

from app.models.route_option import RouteOption
from app.parsers.bing_maps_parser import BingMapsParser, _parse_locator


def _option() -> RouteOption:
    return RouteOption(
        summary="Route",
        distance_text="10 km",
        distance_km=10.0,
        duration_text="20 min",
        duration_minutes=20,
    )


def test_parse_locator_uses_provider_identity() -> None:
    locator = MagicMock()
    locator.inner_text.return_value = "Route\n10 km\n20 min"

    option = _parse_locator(locator)

    assert option is not None
    assert option.raw["provider"] == "bing_maps_web"


def test_parse_returns_routes_and_logs_diagnostics() -> None:
    page = MagicMock()
    locator = MagicMock()
    locator.count.return_value = 2
    diagnostics = MagicMock()

    with (
        patch(
            "app.parsers.bing_maps_parser.BingMapsLocator.route_results",
            return_value=locator,
        ),
        patch(
            "app.parsers.bing_maps_parser._parse_locator",
            side_effect=[_option(), None],
        ),
    ):
        routes = BingMapsParser.parse(page, diagnostics)

    assert routes == [_option()]
    assert locator.nth.call_count == 2
    diagnostics.log_routes.assert_called_once()


def test_parse_respects_max_routes() -> None:
    page = MagicMock()
    locator = MagicMock()
    locator.count.return_value = 99

    with (
        patch(
            "app.parsers.bing_maps_parser.BingMapsLocator.route_results",
            return_value=locator,
        ),
        patch(
            "app.parsers.bing_maps_parser.config.PARSER_MAX_ROUTES",
            1,
        ),
        patch(
            "app.parsers.bing_maps_parser._parse_locator",
            return_value=_option(),
        ) as parse_locator,
    ):
        routes = BingMapsParser.parse(page)

    assert len(routes) == 1
    parse_locator.assert_called_once()


def test_parse_locator_handles_live_bing_vietnamese_unicode() -> None:
    locator = MagicMock()
    locator.inner_text.return_value = (
        "Qua QL 91\n"
        "Tuyến đường nhanh nhất\n"
        "Không chậm trễ\n"
        "Chi tiết\n"
        "2 giờ 46 phút\n"
        "127.2 km"
    )

    option = _parse_locator(locator)

    assert option is not None
    assert option.summary == "Qua QL 91"
    assert option.distance_km == 127.2
    assert option.duration_minutes == 166
