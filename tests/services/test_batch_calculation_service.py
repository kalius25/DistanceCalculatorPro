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
    from app.batch import RetryPolicy

    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(max_attempts=1),
    )

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

    assert (
        service.calculate_queue(
            queue,
            should_stop=lambda: next(checks),
            wait_if_paused=MagicMock(),
        )
        == []
    )
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


def test_calculate_queue_writes_existing_and_processed_results() -> None:
    from app.batch import BatchQueue, RouteJob, RouteJobStatus
    from app.models.route_option import RouteOption

    existing = RouteJob(
        2,
        "A",
        "A",
        "Distance",
        status=RouteJobStatus.DONE,
        result_distance_km=0.0,
    )
    invalid = RouteJob(
        3,
        "10,999",
        "B",
        "Distance",
        status=RouteJobStatus.INVALID,
        validation_error="invalid coordinates",
    )
    pending = RouteJob(4, "C", "D", "Distance")
    queue = BatchQueue([existing, invalid, pending])
    request = make_request("C", "D")
    result = RouteResult(
        True,
        request,
        "Google",
        routes=[RouteOption(distance_km=7.2, duration_minutes=10)],
    )
    calculation_service = MagicMock()
    calculation_service.calculate.return_value = result
    writer = MagicMock()
    service = BatchCalculationService(calculation_service)

    assert service.calculate_queue(queue, result_writer=writer) == [result]
    assert writer.write.call_args_list == [
        __import__("unittest.mock").mock.call(existing),
        __import__("unittest.mock").mock.call(invalid),
        __import__("unittest.mock").mock.call(pending),
    ]
    writer.flush.assert_called_once_with()


def test_calculate_queue_flushes_writer_for_empty_and_exception() -> None:
    from app.batch import BatchQueue, RouteJob

    calculation_service = MagicMock()
    service = BatchCalculationService(calculation_service)
    writer = MagicMock()
    assert (
        service.calculate_queue(
            BatchQueue(),
            result_writer=writer,
        )
        == []
    )
    writer.flush.assert_called_once_with()

    writer.reset_mock()
    calculation_service.calculate.side_effect = RuntimeError("failed")
    queue = BatchQueue([RouteJob(2, "A", "B", "Distance")])
    import pytest

    with pytest.raises(RuntimeError, match="failed"):
        service.calculate_queue(queue, result_writer=writer)
    writer.write.assert_called_once_with(next(iter(queue)))
    writer.flush.assert_called_once_with()


def test_calculate_queue_finishes_batch_when_final_flush_fails() -> None:
    from pathlib import Path

    from app.batch import BatchQueue, OutputWriteError, RouteJob

    calculation_service = MagicMock()
    calculation_service.calculate.return_value = make_result(make_request("A", "B"))
    writer = MagicMock()
    writer.flush.side_effect = OutputWriteError(
        Path("routes.result.xlsx"),
        "replace",
        "locked",
    )
    service = BatchCalculationService(calculation_service)
    queue = BatchQueue([RouteJob(2, "A", "B", "Distance")])

    import pytest

    with pytest.raises(OutputWriteError, match="Unable to replace"):
        service.calculate_queue(queue, result_writer=writer)

    writer.flush.assert_called_once_with()
    calculation_service.finish_batch.assert_called_once_with()


def test_calculate_queue_stops_when_pending_job_disappears() -> None:
    from unittest.mock import PropertyMock

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


def test_calculate_queue_retries_transient_result_then_succeeds() -> None:
    from unittest.mock import call

    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus
    from app.exceptions import ErrorCode
    from app.models.route_option import RouteOption

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    first = RouteResult(
        False,
        make_request("A", "B"),
        "Google",
        error="timeout",
        error_code=ErrorCode.ENGINE_ERROR,
    )
    second = RouteResult(
        True,
        make_request("A", "B"),
        "Google",
        routes=[RouteOption(distance_km=8.6, duration_minutes=20)],
    )
    calculation_service = MagicMock()
    calculation_service.calculate.side_effect = [first, second]
    sleeper = MagicMock()
    callback = MagicMock()
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(
            max_attempts=3,
            initial_delay_seconds=0.2,
            backoff_multiplier=2.0,
            max_delay_seconds=1.0,
        ),
        sleep_callback=sleeper,
    )

    assert service.calculate_queue(queue, progress_callback=callback) == [second]

    assert calculation_service.calculate.call_count == 2
    assert sleeper.call_args_list == [call(0.1), call(0.1)]
    assert job.status is RouteJobStatus.DONE
    assert job.attempt_count == 2
    assert job.retry_count == 1
    assert job.last_error == "timeout"
    assert job.started_at is not None
    assert job.finished_at is not None
    callback.assert_called_once_with(1, 1, job, second)


def test_calculate_queue_exhausts_retries_and_reports_once() -> None:
    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus
    from app.exceptions import ErrorCode

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    failures = [
        RouteResult(
            False,
            make_request("A", "B"),
            "Google",
            error=f"timeout {number}",
            error_code=ErrorCode.ENGINE_ERROR,
        )
        for number in (1, 2, 3)
    ]
    calculation_service = MagicMock()
    calculation_service.calculate.side_effect = failures
    callback = MagicMock()
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(
            max_attempts=3,
            initial_delay_seconds=0,
        ),
    )

    assert service.calculate_queue(queue, progress_callback=callback) == [failures[-1]]

    assert job.status is RouteJobStatus.FAILED
    assert job.attempt_count == 3
    assert job.retry_count == 2
    assert job.last_error == "timeout 3"
    assert job.validation_error == "timeout 3"
    callback.assert_called_once_with(1, 1, job, failures[-1])


def test_calculate_queue_does_not_retry_terminal_result() -> None:
    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus
    from app.exceptions import ErrorCode

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    result = RouteResult(
        False,
        make_request("A", "B"),
        "Google",
        error="parser failed",
        error_code=ErrorCode.PARSER_ERROR,
    )
    calculation_service = MagicMock()
    calculation_service.calculate.return_value = result
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(max_attempts=3, initial_delay_seconds=0),
    )

    assert service.calculate_queue(queue) == [result]
    calculation_service.calculate.assert_called_once()
    assert job.status is RouteJobStatus.FAILED
    assert job.attempt_count == 1
    assert job.retry_count == 0


def test_calculate_queue_retries_transient_exception_and_reraises_terminal() -> None:
    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    success = make_result(make_request("A", "B"))
    calculation_service = MagicMock()
    calculation_service.calculate.side_effect = [TimeoutError("timeout"), success]
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0),
    )

    assert service.calculate_queue(queue) == [success]
    assert job.status is RouteJobStatus.DONE
    assert job.attempt_count == 2
    assert job.retry_count == 1

    terminal_job = RouteJob(3, "C", "D", "Distance")
    terminal_queue = BatchQueue([terminal_job])
    calculation_service.calculate.side_effect = RuntimeError("permanent failure")

    import pytest

    with pytest.raises(RuntimeError, match="permanent failure"):
        service.calculate_queue(terminal_queue)
    assert terminal_job.status is RouteJobStatus.FAILED
    assert terminal_job.attempt_count == 1
    assert terminal_job.last_error == "permanent failure"
    assert terminal_job.finished_at is not None


def test_calculate_queue_stop_during_retry_returns_job_to_pending() -> None:
    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus
    from app.exceptions import ErrorCode

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    result = RouteResult(
        False,
        make_request("A", "B"),
        "Google",
        error="timeout",
        error_code=ErrorCode.ENGINE_ERROR,
    )
    calculation_service = MagicMock()
    calculation_service.calculate.return_value = result
    checks = iter([False, False, True])
    wait = MagicMock()
    sleeper = MagicMock()
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(
            max_attempts=3,
            initial_delay_seconds=1,
        ),
        sleep_callback=sleeper,
    )

    assert (
        service.calculate_queue(
            queue,
            should_stop=lambda: next(checks),
            wait_if_paused=wait,
        )
        == []
    )

    assert job.status is RouteJobStatus.PENDING
    assert job.attempt_count == 1
    assert job.retry_count == 1
    assert sleeper.call_count == 0
    assert wait.call_count == 2


def test_calculate_queue_stop_after_retryable_exception_requeues_job() -> None:
    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    calculation_service = MagicMock()
    calculation_service.calculate.side_effect = TimeoutError("timeout")
    checks = iter([False, False, True])
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(max_attempts=2, initial_delay_seconds=1),
        sleep_callback=MagicMock(),
    )

    assert (
        service.calculate_queue(
            queue,
            should_stop=lambda: next(checks),
        )
        == []
    )
    assert job.status is RouteJobStatus.PENDING
    assert job.attempt_count == 1
    assert job.retry_count == 1


def test_calculate_queue_stop_after_zero_retry_delay_requeues_job() -> None:
    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus
    from app.exceptions import ErrorCode

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    result = RouteResult(
        False,
        make_request("A", "B"),
        "Google",
        error="timeout",
        error_code=ErrorCode.ENGINE_ERROR,
    )
    calculation_service = MagicMock()
    calculation_service.calculate.return_value = result
    checks = iter([False, False, True])
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0),
    )

    assert (
        service.calculate_queue(
            queue,
            should_stop=lambda: next(checks),
        )
        == []
    )
    assert job.status is RouteJobStatus.PENDING
    assert job.attempt_count == 1
    assert job.retry_count == 1


def test_calculate_queue_preserves_resumed_existing_results() -> None:
    from app.batch import BatchQueue, RouteJob, RouteJobStatus

    resumed = RouteJob(
        2,
        "A",
        "B",
        "Distance",
        status=RouteJobStatus.DONE,
        result_distance_km=8.6,
        metadata={"resumed_existing_result": True},
    )
    zero_distance = RouteJob(
        3,
        "C",
        "C",
        "Distance",
        status=RouteJobStatus.DONE,
        result_distance_km=0.0,
    )
    queue = BatchQueue([resumed, zero_distance])
    calculation_service = MagicMock()
    writer = MagicMock()

    service = BatchCalculationService(calculation_service)

    assert service.calculate_queue(queue, result_writer=writer) == []
    writer.write.assert_called_once_with(zero_distance)
    writer.flush.assert_called_once_with()
    calculation_service.start_batch.assert_not_called()


def test_calculate_queue_emits_row_events_for_retry_lifecycle() -> None:
    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus
    from app.exceptions import ErrorCode
    from app.models.route_option import RouteOption

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    retryable = RouteResult(
        False,
        make_request("A", "B"),
        "Google",
        error="timeout",
        error_code=ErrorCode.ENGINE_ERROR,
    )
    success = RouteResult(
        True,
        make_request("A", "B"),
        "Google",
        routes=[RouteOption(distance_km=8.6, duration_minutes=20)],
    )
    calculation_service = MagicMock()
    calculation_service.calculate.side_effect = [retryable, success]
    events = []
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(max_attempts=2, initial_delay_seconds=0),
    )

    assert service.calculate_queue(queue, row_event_callback=events.append) == [success]

    assert [event.status for event in events] == [
        RouteJobStatus.RUNNING,
        RouteJobStatus.RETRY,
        RouteJobStatus.RUNNING,
        RouteJobStatus.DONE,
    ]
    assert [event.attempt_count for event in events] == [0, 1, 1, 2]
    assert [event.retry_count for event in events] == [0, 1, 1, 1]
    assert all(event.preview_row_index == 0 for event in events)


def test_calculate_queue_emits_pending_when_stopped_during_retry() -> None:
    from app.batch import BatchQueue, RetryPolicy, RouteJob, RouteJobStatus
    from app.exceptions import ErrorCode

    job = RouteJob(2, "A", "B", "Distance")
    queue = BatchQueue([job])
    result = RouteResult(
        False,
        make_request("A", "B"),
        "Google",
        error="timeout",
        error_code=ErrorCode.ENGINE_ERROR,
    )
    calculation_service = MagicMock()
    calculation_service.calculate.return_value = result
    checks = iter([False, False, True])
    events = []
    service = BatchCalculationService(
        calculation_service,
        retry_policy=RetryPolicy(max_attempts=2, initial_delay_seconds=1),
        sleep_callback=MagicMock(),
    )

    assert (
        service.calculate_queue(
            queue,
            should_stop=lambda: next(checks),
            row_event_callback=events.append,
        )
        == []
    )

    assert [event.status for event in events] == [
        RouteJobStatus.RUNNING,
        RouteJobStatus.RETRY,
        RouteJobStatus.PENDING,
    ]
