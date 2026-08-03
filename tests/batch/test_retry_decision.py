import pytest

from app.batch import RetryDecision
from app.exceptions import (
    EngineException,
    ErrorCode,
    ParserException,
    ProviderException,
    ValidationException,
)
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult


def make_result(
    *,
    success: bool = False,
    error: str = "",
    error_code: ErrorCode | None = None,
    exception: Exception | None = None,
) -> RouteResult:
    return RouteResult(
        success=success,
        request=RouteRequest(origin="A", destination="B"),
        provider="Google",
        error=error,
        error_code=error_code,
        exception=exception,
    )


@pytest.mark.parametrize(
    "error_code",
    [
        ErrorCode.ENGINE_ERROR,
        ErrorCode.NETWORK_ERROR,
        ErrorCode.PROVIDER_ERROR,
    ],
)
def test_retry_decision_accepts_transient_error_codes(
    error_code: ErrorCode,
) -> None:
    assert RetryDecision().should_retry_result(make_result(error_code=error_code))


def test_retry_decision_rejects_success_and_terminal_failures() -> None:
    decision = RetryDecision()

    assert not decision.should_retry_result(make_result(success=True))
    assert not decision.should_retry_result(
        make_result(error_code=ErrorCode.PARSER_ERROR)
    )
    assert not decision.should_retry_result(make_result(error="invalid route"))


@pytest.mark.parametrize(
    "error",
    [
        EngineException("engine"),
        ProviderException("provider"),
        TimeoutError("timeout"),
        ConnectionError("network"),
        RuntimeError("HTTP 503 temporarily unavailable"),
    ],
)
def test_retry_decision_accepts_transient_exceptions(error: Exception) -> None:
    assert RetryDecision().should_retry_exception(error)


@pytest.mark.parametrize(
    "error",
    [
        ParserException("parser"),
        ValidationException("validation"),
        RuntimeError("permanent failure"),
    ],
)
def test_retry_decision_rejects_terminal_exceptions(error: Exception) -> None:
    assert not RetryDecision().should_retry_exception(error)


def test_retry_decision_uses_result_exception_and_message_keywords() -> None:
    decision = RetryDecision()

    assert decision.should_retry_result(
        make_result(exception=TimeoutError("request timed out"))
    )
    assert decision.should_retry_result(make_result(error="Target page closed"))
