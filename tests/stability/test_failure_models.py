import pytest

from app.stability import (
    FailureEvent,
    FailureKind,
    RecoveryCycleResult,
    RecoveryEventResult,
    RecoveryRunResult,
)
from app.stability.models import LeakSnapshot

pytestmark = [pytest.mark.stability, pytest.mark.failure_injection]


def snapshot(memory: int = 0) -> LeakSnapshot:
    return LeakSnapshot("now", memory, memory, 1, ("Main",), (0, 0, 0), 0, 1)


def test_failure_event_validates_cycle() -> None:
    with pytest.raises(ValueError, match="cannot be negative"):
        FailureEvent(-1, FailureKind.PROVIDER_TIMEOUT)


def test_recovery_models_compute_counts_and_payloads() -> None:
    recovered = RecoveryEventResult(
        0,
        FailureKind.PROVIDER_TIMEOUT,
        1,
        True,
        "timeout",
        "retry",
    )
    failed = RecoveryEventResult(
        1,
        FailureKind.PARSER_FAILURE,
        1,
        False,
        "parse",
        "abort_cycle",
    )
    first = RecoveryCycleResult(0, 2, 10, True, (recovered,))
    second = RecoveryCycleResult(1, 1, 0, False, (failed,), "parse")
    result = RecoveryRunResult(
        "mixed",
        2,
        10,
        snapshot(),
        snapshot(),
        (first, second),
    )

    assert first.passed
    assert not second.passed
    assert result.recovered_failures == 1
    assert result.unrecovered_failures == 1
    assert result.completed_rows == 10
    assert not result.passed
    payload = result.to_dict()
    assert payload["cycle_results"][0]["events"][0]["kind"] == "provider_timeout"


def test_recovery_run_passes_without_failures_or_violations() -> None:
    cycle = RecoveryCycleResult(0, 1, 4, True)
    result = RecoveryRunResult("clean", 1, 4, snapshot(), snapshot(), (cycle,))

    assert result.passed
