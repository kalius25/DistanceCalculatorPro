from types import SimpleNamespace
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.services.calculation_service import CalculationService


def make_request(
    origin="A",
    destination="B",
):
    return RouteRequest(
        origin=origin,
        destination=destination,
    )


def make_route(minutes):
    return RouteOption(
        summary=f"{minutes} min",
        distance_km=10,
        duration_minutes=minutes,
    )


def test_constructor():
    provider = MagicMock()

    service = CalculationService(provider)

    assert service.provider is provider


def test_validate_success():
    request = make_request()

    CalculationService._validate(request)


def test_validate_empty_origin():
    request = make_request(origin="   ")

    with pytest.raises(ValueError, match="Origin is empty"):
        CalculationService._validate(request)


def test_validate_empty_destination():
    request = make_request(destination=" ")

    with pytest.raises(ValueError, match="Destination is empty"):
        CalculationService._validate(request)


def test_select_best_route_single():
    result = RouteResult(
        success=True,
        request=make_request(),
        provider="Test",
        routes=[
            make_route(30),
        ],
    )

    assert CalculationService._select_best_route(result) == 0


def test_select_best_route_multiple():
    result = RouteResult(
        success=True,
        request=make_request(),
        provider="Test",
        routes=[
            make_route(35),
            make_route(18),
            make_route(25),
        ],
    )

    assert CalculationService._select_best_route(result) == 1


def test_calculate_success_without_routes():
    request = make_request()

    provider = MagicMock()

    provider.calculate.return_value = RouteResult(
        success=True,
        request=request,
        provider="Google",
        routes=[],
    )

    service = CalculationService(provider)

    result = service.calculate(request)

    provider.calculate.assert_called_once_with(request)
    assert result.success is True
    assert result.selected_route == 0


def test_calculate_success_with_routes():
    request = make_request()

    provider = MagicMock()

    provider.calculate.return_value = RouteResult(
        success=True,
        request=request,
        provider="Google",
        routes=[
            make_route(30),
            make_route(10),
            make_route(20),
        ],
    )

    service = CalculationService(provider)

    result = service.calculate(request)

    assert result.selected_route == 1
    assert result.best_route.duration_minutes == 10


def test_calculate_provider_exception():
    request = make_request()

    provider = MagicMock()
    provider.calculate.side_effect = RuntimeError("boom")

    service = CalculationService(provider)

    with patch(
        "app.services.calculation_service.traceback.print_exc"
    ):
        result = service.calculate(request)

    assert result.success is False
    assert result.request is request
    assert result.provider == provider.__class__.__name__
    assert result.error == "boom"


def test_calculate_validation_exception():
    request = make_request(origin="")

    provider = MagicMock()

    service = CalculationService(provider)

    with patch(
        "app.services.calculation_service.traceback.print_exc"
    ):
        result = service.calculate(request)

    provider.calculate.assert_not_called()

    assert result.success is False
    assert result.error == "Origin is empty."