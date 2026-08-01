from unittest.mock import MagicMock, PropertyMock

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
    requests = (make_request(f"A{i}", f"B{i}") for i in range(3))

    calculation_service = MagicMock()

    calculation_service.calculate.side_effect = lambda request: make_result(request)

    service = BatchCalculationService(calculation_service)

    results = service.calculate(requests)

    assert len(results) == 3

    assert calculation_service.calculate.call_count == 3


def test_calculate_stops_before_and_after_pause_callback():
    request = make_request("A", "B")
    calculation_service = MagicMock()
    service = BatchCalculationService(calculation_service)

    results = service.calculate([request], should_stop=lambda: True)
    assert results == []

    checks = iter([False, True])
    wait = MagicMock()
    results = service.calculate(
        [request],
        should_stop=lambda: next(checks),
        wait_if_paused=wait,
    )
    assert results == []
    wait.assert_called_once_with()
    calculation_service.calculate.assert_not_called()


def test_calculate_waits_before_processing():
    request = make_request("A", "B")
    result = make_result(request)
    calculation_service = MagicMock()
    calculation_service.calculate.return_value = result
    wait = MagicMock()
    service = BatchCalculationService(calculation_service)

    assert service.calculate([request], wait_if_paused=wait) == [result]
    wait.assert_called_once_with()


def test_calculate_wraps_non_empty_requests_in_batch_lifecycle():
    request = make_request("A", "B")
    result = make_result(request)
    calculation_service = MagicMock()
    calculation_service.calculate.return_value = result
    service = BatchCalculationService(calculation_service)

    assert service.calculate([request]) == [result]
    calculation_service.start_batch.assert_called_once_with()
    calculation_service.finish_batch.assert_called_once_with()


def test_calculate_finishes_batch_when_calculation_raises():
    request = make_request("A", "B")
    calculation_service = MagicMock()
    calculation_service.calculate.side_effect = RuntimeError("failed")
    service = BatchCalculationService(calculation_service)

    import pytest
    with pytest.raises(RuntimeError, match="failed"):
        service.calculate([request])
    calculation_service.finish_batch.assert_called_once_with()


def test_calculate_queue_updates_job_states_and_relays_progress():
    from app.batch import BatchQueue, RouteJob, RouteJobStatus
    from app.models.route_option import RouteOption

    first = RouteJob(2, "A", "B", "Distance")
    second = RouteJob(3, "C", "D", "Distance")
    queue = BatchQueue([first, second])
    success = RouteResult(
        True,
        make_request("A", "B"),
        "Google",
        routes=[RouteOption(distance_km=8.6, duration_minutes=20)],
    )
    failure = RouteResult(
        False,
        make_request("C", "D"),
        "Google",
        error="timeout",
    )
    calculation_service = MagicMock()
    calculation_service.calculate.side_effect = [success, failure]
    callback = MagicMock()
    service = BatchCalculationService(calculation_service)

    results = service.calculate_queue(queue, progress_callback=callback)

    assert results == [success, failure]
    assert first.status is RouteJobStatus.DONE
    assert first.result_distance_km == 8.6
    assert second.status is RouteJobStatus.FAILED
    assert second.validation_error == "timeout"
    assert queue.pending_count == 0
    assert queue.done_count == 1
    assert queue.failed_count == 1
    assert queue.terminal_count == 2
    callback.assert_any_call(1, 2, first, success)
    callback.assert_any_call(2, 2, second, failure)
    calculation_service.start_batch.assert_called_once_with()
    calculation_service.finish_batch.assert_called_once_with()


def test_calculate_queue_handles_empty_stop_pause_and_missing_best_route():
    from app.batch import BatchQueue, RouteJob, RouteJobStatus

    calculation_service = MagicMock()
    service = BatchCalculationService(calculation_service)
    assert service.calculate_queue(BatchQueue()) == []
    calculation_service.start_batch.assert_not_called()

    stopped_job = RouteJob(2, "A", "B", "Distance")
    stopped_queue = BatchQueue([stopped_job])
    assert service.calculate_queue(stopped_queue, should_stop=lambda: True) == []
    assert stopped_job.status is RouteJobStatus.PENDING

    job = RouteJob(3, "C", "D", "Distance", metadata={"source": "sheet"})
    queue = BatchQueue([job])
    wait = MagicMock()
    result = RouteResult(True, make_request("C", "D"), "Google")
    calculation_service.calculate.return_value = result

    assert service.calculate_queue(queue, wait_if_paused=wait) == [result]
    wait.assert_called_once_with()
    assert job.status is RouteJobStatus.DONE
    assert job.result_distance_km is None
    request = calculation_service.calculate.call_args.args[0]
    assert request.metadata == {
        "source": "sheet",
        "row_number": 3,
        "result_column": "Distance",
    }


def test_calculate_queue_stops_after_pause_and_marks_unexpected_failure():
    from app.batch import BatchQueue, RouteJob, RouteJobStatus

    calculation_service = MagicMock()
    service = BatchCalculationService(calculation_service)
    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    checks = iter([False, True])

    assert service.calculate_queue(
        queue,
        should_stop=lambda: next(checks),
        wait_if_paused=MagicMock(),
    ) == []
    assert job.status is RouteJobStatus.PENDING

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    calculation_service.calculate.side_effect = RuntimeError("browser crashed")
    import pytest

    with pytest.raises(RuntimeError, match="browser crashed"):
        service.calculate_queue(queue)
    assert job.status is RouteJobStatus.FAILED
    assert job.validation_error == "browser crashed"
    calculation_service.finish_batch.assert_called()

def test_calculate_queue_stops_when_pending_job_disappears() -> None:
    from app.batch import BatchQueue

    calculation_service = MagicMock()
    service = BatchCalculationService(calculation_service)

    queue = MagicMock(spec=BatchQueue)
    type(queue).pending_count = PropertyMock(return_value=1)
    queue.next_pending.return_value = None

    results = service.calculate_queue(queue)

    assert results == []
    queue.next_pending.assert_called_once_with()
    calculation_service.calculate.assert_not_called()
    calculation_service.start_batch.assert_called_once_with()
    calculation_service.finish_batch.assert_called_once_with()