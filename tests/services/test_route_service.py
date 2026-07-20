from __future__ import annotations

from unittest.mock import create_autospec

import pytest

from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider
from app.services.route_service import RouteService


# ==========================================================
# Helpers
# ==========================================================


def make_request(
    origin: str = "A",
    destination: str = "B",
) -> RouteRequest:
    return RouteRequest(
        origin=origin,
        destination=destination,
    )


def make_option(
    duration: int,
    distance: float,
) -> RouteOption:
    return RouteOption(
        duration_minutes=duration,
        distance_km=distance,
    )


def make_result(
    routes: list[RouteOption] | None = None,
    *,
    success: bool = True,
) -> RouteResult:
    return RouteResult(
        success=success,
        request=make_request(),
        provider="mock",
        routes=routes or [],
    )


def make_provider():
    return create_autospec(BaseProvider, instance=True)


# ==========================================================
# Validation
# ==========================================================


@pytest.mark.parametrize(
    "origin",
    [
        "",
        " ",
        "   ",
    ],
)
def test_calculate_origin_empty(origin: str) -> None:
    provider = make_provider()
    service = RouteService(provider)

    result = service.calculate(
        make_request(
            origin=origin,
            destination="B",
        )
    )

    assert result.success is False
    assert result.error == "Origin is empty."

    provider.calculate.assert_not_called()


@pytest.mark.parametrize(
    "destination",
    [
        "",
        " ",
        "   ",
    ],
)
def test_calculate_destination_empty(
    destination: str,
) -> None:
    provider = make_provider()
    service = RouteService(provider)

    result = service.calculate(
        make_request(
            origin="A",
            destination=destination,
        )
    )

    assert result.success is False
    assert result.error == "Destination is empty."

    provider.calculate.assert_not_called()


@pytest.mark.parametrize(
    ("origin", "destination"),
    [
        ("A", "A"),
        (" abc ", "abc"),
    ],
)
def test_calculate_same_location(
    origin: str,
    destination: str,
) -> None:
    provider = make_provider()
    service = RouteService(provider)

    result = service.calculate(
        make_request(origin, destination)
    )

    assert result.success is False
    assert (
        result.error
        == "Origin and destination cannot be the same."
    )

    provider.calculate.assert_not_called()


# ==========================================================
# Provider
# ==========================================================


def test_provider_failure() -> None:
    provider = make_provider()

    provider.calculate.return_value = make_result(
        success=False,
    )

    service = RouteService(provider)

    result = service.calculate(make_request())

    assert result.success is False

    provider.calculate.assert_called_once()


# ==========================================================
# Best Route
# ==========================================================


def test_select_shortest_duration() -> None:
    routes = [
        make_option(30, 15),
        make_option(20, 50),
        make_option(40, 10),
    ]

    provider = make_provider()

    provider.calculate.return_value = make_result(routes)

    service = RouteService(provider)

    result = service.calculate(make_request())

    assert result.selected_route == 1
    assert result.best_route is routes[1]


def test_select_shortest_distance_when_duration_equal() -> None:
    routes = [
        make_option(20, 10),
        make_option(20, 8),
        make_option(20, 12),
    ]

    provider = make_provider()

    provider.calculate.return_value = make_result(routes)

    service = RouteService(provider)

    result = service.calculate(make_request())

    assert result.selected_route == 1
    assert result.best_route is routes[1]


def test_empty_routes() -> None:
    provider = make_provider()

    provider.calculate.return_value = make_result([])

    service = RouteService(provider)

    result = service.calculate(make_request())

    assert result.success is True
    assert result.routes == []
    assert result.best_route is None
    assert result.selected_route == 0


def test_single_route() -> None:
    route = make_option(
        duration=25,
        distance=12,
    )

    provider = make_provider()

    provider.calculate.return_value = make_result([route])

    service = RouteService(provider)

    result = service.calculate(make_request())

    assert result.selected_route == 0
    assert result.best_route is route


# ==========================================================
# Request trimming
# ==========================================================


@pytest.mark.parametrize(
    ("origin", "destination"),
    [
        ("   A", "B"),
        ("A", "   B"),
        ("   A   ", "   B   "),
    ],
)
def test_request_strip_before_validation(
    origin: str,
    destination: str,
) -> None:
    provider = make_provider()

    provider.calculate.return_value = make_result()

    service = RouteService(provider)

    result = service.calculate(
        make_request(origin, destination)
    )

    assert result.success is True

    provider.calculate.assert_called_once()