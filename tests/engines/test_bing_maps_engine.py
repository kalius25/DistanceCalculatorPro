from unittest.mock import MagicMock, patch

import pytest
from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.engines.bing_maps_engine import BingMapsEngine
from app.enums.travel_mode import TravelMode
from app.exceptions import EngineException
from app.models.route_request import RouteRequest


@pytest.fixture
def route_request() -> RouteRequest:
    return RouteRequest(
        origin="10.113922624804262,105.69436247381175",
        destination="10.892645,105.041044",
        travel_mode=TravelMode.DRIVING,
    )


def test_constructor_rejects_non_positive_timeout() -> None:
    with pytest.raises(
        ValueError,
        match="action timeout must be greater than zero",
    ):
        BingMapsEngine(0)


def test_navigate_opens_complete_bing_url(
    route_request: RouteRequest,
) -> None:
    page = MagicMock()
    diagnostics = MagicMock()
    engine = BingMapsEngine(15_000, diagnostics)

    url = engine.navigate(page, route_request)

    assert url == (
        "https://www.bing.com/maps/directions"
        "?style=r"
        "&rtp=pos.10.113922624804262_105.69436247381175"
        "~pos.10.892645_105.041044"
        "&mode=d"
    )
    page.goto.assert_called_once_with(
        url,
        timeout=15_000,
        wait_until="domcontentloaded",
    )
    assert diagnostics.trace_browser.call_count == 2


def test_navigate_wraps_playwright_timeout(
    route_request: RouteRequest,
) -> None:
    page = MagicMock()
    page.goto.side_effect = PlaywrightTimeoutError("timeout")
    engine = BingMapsEngine(15_000, MagicMock())

    with pytest.raises(
        EngineException,
        match="Bing Maps request timed out",
    ) as error:
        engine.navigate(page, route_request)

    assert error.value.context["origin"] == route_request.origin
    assert error.value.context["destination"] == route_request.destination


def test_navigate_wraps_playwright_error(
    route_request: RouteRequest,
) -> None:
    page = MagicMock()
    page.goto.side_effect = PlaywrightError("browser")
    engine = BingMapsEngine(15_000, MagicMock())

    with pytest.raises(
        EngineException,
        match="Bing Maps browser operation failed",
    ):
        engine.navigate(page, route_request)


def test_default_diagnostics_manager_is_created() -> None:
    diagnostics = MagicMock()

    with patch(
        "app.engines.bing_maps_engine.DiagnosticsManager",
        return_value=diagnostics,
    ):
        engine = BingMapsEngine(15_000)

    assert engine._diagnostics is diagnostics


def test_find_routes_waits_and_parses(
    route_request: RouteRequest,
) -> None:
    page = MagicMock()
    engine = BingMapsEngine(15_000, MagicMock())
    routes = [MagicMock()]

    with (
        patch(
            "app.engines.bing_maps_engine." "BingMapsLocator.route_results",
            return_value=page.locator.return_value,
        ),
        patch(
            "app.engines.bing_maps_engine." "BingMapsParser.parse",
            return_value=routes,
        ) as parser,
    ):
        result = engine.find_routes(page, route_request)

    assert result == routes
    page.locator.return_value.first.wait_for.assert_called_once_with(
        state="visible",
        timeout=15_000,
    )
    parser.assert_called_once_with(page, engine._diagnostics)


def test_find_routes_rejects_empty_parse(
    route_request: RouteRequest,
) -> None:
    page = MagicMock()
    engine = BingMapsEngine(15_000, MagicMock())

    with (
        patch(
            "app.engines.bing_maps_engine." "BingMapsLocator.route_results",
            return_value=page.locator.return_value,
        ),
        patch(
            "app.engines.bing_maps_engine." "BingMapsParser.parse",
            return_value=[],
        ),
    ):
        with pytest.raises(
            EngineException,
            match="Bing Maps returned no parseable routes",
        ):
            engine.find_routes(page, route_request)


def test_find_routes_wraps_result_timeout(
    route_request: RouteRequest,
) -> None:
    page = MagicMock()
    page.locator.return_value.first.wait_for.side_effect = PlaywrightTimeoutError(
        "results"
    )
    engine = BingMapsEngine(15_000, MagicMock())

    with patch(
        "app.engines.bing_maps_engine." "BingMapsLocator.route_results",
        return_value=page.locator.return_value,
    ):
        with pytest.raises(
            EngineException,
            match="Bing Maps route results timed out",
        ):
            engine.find_routes(page, route_request)


def test_find_routes_wraps_result_playwright_error(
    route_request: RouteRequest,
) -> None:
    page = MagicMock()
    page.locator.return_value.first.wait_for.side_effect = PlaywrightError("results")
    engine = BingMapsEngine(15_000, MagicMock())

    with patch(
        "app.engines.bing_maps_engine." "BingMapsLocator.route_results",
        return_value=page.locator.return_value,
    ):
        with pytest.raises(
            EngineException,
            match="Bing Maps result extraction failed",
        ):
            engine.find_routes(page, route_request)


def test_context_contains_route_identity(
    route_request: RouteRequest,
) -> None:
    context = BingMapsEngine._context(
        route_request,
        "https://example.test",
    )

    assert context == {
        "origin": route_request.origin,
        "destination": route_request.destination,
        "travel_mode": route_request.travel_mode.value,
        "url": "https://example.test",
    }
