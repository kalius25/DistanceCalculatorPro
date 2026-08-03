from enum import Enum
from unittest.mock import MagicMock

import pytest

import app.services.calculation_service as calculation_service_module
from app.exceptions import ErrorCode, ProviderException, ValidationException
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

    with pytest.raises(
        ValidationException,
        match="Origin is empty.",
    ) as exc:
        CalculationService._validate(request)

    assert exc.value.error_code is ErrorCode.VALIDATION_ERROR
    assert exc.value.context == {
        "field": "origin",
    }


def test_validate_empty_destination():
    request = make_request(destination=" ")

    with pytest.raises(
        ValidationException,
        match="Destination is empty.",
    ) as exc:
        CalculationService._validate(request)

    assert exc.value.error_code is ErrorCode.VALIDATION_ERROR
    assert exc.value.context == {
        "field": "destination",
    }


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

    with pytest.raises(RuntimeError, match="boom"):
        service.calculate(request)


def test_calculate_validation_exception():
    request = make_request(origin="")

    provider = MagicMock()

    service = CalculationService(provider)

    with pytest.raises(
        ValidationException,
        match="Origin is empty.",
    ):
        service.calculate(request)

    provider.calculate.assert_not_called()


def test_calculate_returns_and_logs_failed_provider_result(
    monkeypatch,
):
    request = make_request()

    provider_exception = RuntimeError(
        "Provider failed.",
    )

    failed_result = RouteResult(
        success=False,
        request=request,
        provider="google_web",
        error="Provider failed.",
        error_code=ErrorCode.PROVIDER_ERROR,
        context={
            "provider": "google_web",
        },
        exception=provider_exception,
    )

    provider = MagicMock()
    provider.calculate.return_value = failed_result

    calculation_failed = MagicMock()

    monkeypatch.setattr(
        calculation_service_module.LoggingEvents,
        "calculation_failed",
        calculation_failed,
    )

    service = CalculationService(provider)

    result = service.calculate(request)

    assert result is failed_result

    provider.calculate.assert_called_once_with(
        request,
    )

    calculation_failed.assert_called_once_with(
        calculation_service_module.logger,
        provider="google_web",
        error_code="PROVIDER_ERROR",
        error_message="Provider failed.",
        exception=provider_exception,
    )


def test_calculate_failed_result_uses_provider_class_name(
    monkeypatch,
):
    request = make_request()

    failed_result = RouteResult(
        success=False,
        request=request,
        provider="",
        error="Unknown provider error.",
        error_code=None,
        exception=None,
    )

    provider = MagicMock()
    provider.calculate.return_value = failed_result

    calculation_failed = MagicMock()

    monkeypatch.setattr(
        calculation_service_module.LoggingEvents,
        "calculation_failed",
        calculation_failed,
    )

    service = CalculationService(provider)

    result = service.calculate(request)

    assert result is failed_result

    calculation_failed.assert_called_once_with(
        calculation_service_module.logger,
        provider="MagicMock",
        error_code="UNKNOWN_ERROR",
        error_message="Unknown provider error.",
        exception=None,
    )


def test_calculate_failed_result_uses_fallback_values(
    monkeypatch,
):
    request = make_request()

    failed_result = RouteResult(
        success=False,
        request=request,
        provider="",
        error=None,
        error_code=None,
        exception=None,
    )

    provider = MagicMock()
    provider.calculate.return_value = failed_result

    calculation_failed = MagicMock()

    monkeypatch.setattr(
        calculation_service_module.LoggingEvents,
        "calculation_failed",
        calculation_failed,
    )

    service = CalculationService(provider)

    result = service.calculate(request)

    assert result is failed_result

    calculation_failed.assert_called_once_with(
        calculation_service_module.logger,
        provider="MagicMock",
        error_code="UNKNOWN_ERROR",
        error_message="Unknown error.",
        exception=None,
    )


def test_validate_origin_equals_destination():
    request = make_request(
        origin="Can Tho",
        destination="Can Tho",
    )

    with pytest.raises(
        ValidationException,
        match="Origin and destination cannot be the same.",
    ) as exc:
        CalculationService._validate(request)

    assert exc.value.error_code is ErrorCode.VALIDATION_ERROR
    assert exc.value.context == {
        "origin": "Can Tho",
        "destination": "Can Tho",
    }


def test_validate_origin_equals_destination_after_strip():
    request = make_request(
        origin="  Can Tho ",
        destination="Can Tho",
    )

    with pytest.raises(
        ValidationException,
        match="Origin and destination cannot be the same.",
    ):
        CalculationService._validate(request)


class SampleErrorCode(Enum):
    ENGINE_ERROR = "ENGINE_ERROR"


def test_calculate_distance_calculator_exception():
    request = make_request()

    provider = MagicMock()

    provider.calculate.side_effect = ProviderException(
        "Provider failed.",
        context={
            "provider": "google",
        },
    )

    service = CalculationService(provider)

    result = service.calculate(request)

    assert result.success is False
    assert result.request is request
    assert result.error == "Provider failed."
    assert result.context == {
        "provider": "google",
    }
    assert isinstance(
        result.exception,
        ProviderException,
    )


def test_batch_lifecycle_is_delegated_to_provider():
    provider = MagicMock()
    service = CalculationService(provider)

    service.start_batch()
    service.finish_batch()

    provider.start_batch.assert_called_once_with()
    provider.finish_batch.assert_called_once_with()
