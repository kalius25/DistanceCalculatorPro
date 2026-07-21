from unittest.mock import MagicMock

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.services.batch_calculation_service import BatchCalculationService


def make_request(origin, destination):
    return RouteRequest(
        origin=origin,
        destination=destination,
    )


def make_result(request):
    return RouteResult(
        success=True,
        request=request,
        provider="Google",
    )


def test_constructor():
    calculation_service = MagicMock()

    service = BatchCalculationService(calculation_service)

    assert service.calculation_service is calculation_service


def test_calculate_empty_requests():
    calculation_service = MagicMock()

    service = BatchCalculationService(calculation_service)

    results = service.calculate([])

    assert results == []

    calculation_service.calculate.assert_not_called()


def test_calculate_without_callback():
    request1 = make_request("A", "B")
    request2 = make_request("C", "D")

    result1 = make_result(request1)
    result2 = make_result(request2)

    calculation_service = MagicMock()

    calculation_service.calculate.side_effect = [
        result1,
        result2,
    ]

    service = BatchCalculationService(calculation_service)

    results = service.calculate(
        [
            request1,
            request2,
        ]
    )

    assert results == [
        result1,
        result2,
    ]

    assert calculation_service.calculate.call_count == 2


def test_calculate_with_callback():
    request1 = make_request("A", "B")
    request2 = make_request("C", "D")

    result1 = make_result(request1)
    result2 = make_result(request2)

    calculation_service = MagicMock()

    calculation_service.calculate.side_effect = [
        result1,
        result2,
    ]

    callback = MagicMock()

    service = BatchCalculationService(calculation_service)

    results = service.calculate(
        [
            request1,
            request2,
        ],
        progress_callback=callback,
    )

    assert results == [
        result1,
        result2,
    ]

    assert callback.call_count == 2

    callback.assert_any_call(
        1,
        2,
        request1,
        result1,
    )

    callback.assert_any_call(
        2,
        2,
        request2,
        result2,
    )


def test_calculate_generator():
    requests = (
        make_request(f"A{i}", f"B{i}")
        for i in range(3)
    )

    calculation_service = MagicMock()

    calculation_service.calculate.side_effect = (
        lambda request: make_result(request)
    )

    service = BatchCalculationService(calculation_service)

    results = service.calculate(requests)

    assert len(results) == 3

    assert calculation_service.calculate.call_count == 3