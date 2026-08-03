import pytest

from app.providers.request_pacing import (
    AdaptiveRequestPacer,
    RequestPacingPolicy,
)


def test_request_pacing_policy_validation() -> None:
    with pytest.raises(ValueError, match="Minimum"):
        RequestPacingPolicy(minimum_delay_seconds=-1.0)
    with pytest.raises(ValueError, match="Maximum"):
        RequestPacingPolicy(
            minimum_delay_seconds=2.0,
            maximum_delay_seconds=1.0,
        )
    with pytest.raises(ValueError, match="Initial"):
        RequestPacingPolicy(initial_delay_seconds=3.0)
    with pytest.raises(ValueError, match="Failure"):
        RequestPacingPolicy(failure_increase_seconds=0.0)
    with pytest.raises(ValueError, match="Success"):
        RequestPacingPolicy(success_decrease_seconds=0.0)


def test_adaptive_pacer_increases_decreases_waits_and_resets() -> None:
    waits: list[float] = []
    pacer = AdaptiveRequestPacer(
        RequestPacingPolicy(
            initial_delay_seconds=0.5,
            minimum_delay_seconds=0.0,
            maximum_delay_seconds=1.0,
            failure_increase_seconds=0.4,
            success_decrease_seconds=0.25,
        ),
        sleeper=waits.append,
    )

    pacer.wait()
    pacer.record_failure()
    pacer.record_failure()
    pacer.wait()
    pacer.record_success()
    pacer.record_success()
    pacer.record_success()
    pacer.wait()

    snapshot = pacer.snapshot
    assert waits == [0.5, 1.0, 0.25]
    assert snapshot.waits == 3
    assert snapshot.total_wait_seconds == 1.75
    assert snapshot.current_delay_seconds == 0.25
    assert snapshot.increases == 2
    assert snapshot.decreases == 3

    pacer.record_success()
    pacer.wait()
    assert pacer.snapshot.current_delay_seconds == 0.0

    pacer.reset()
    reset = pacer.snapshot
    assert reset.current_delay_seconds == 0.5
    assert reset.waits == 0
    assert reset.increases == 0
    assert reset.decreases == 0


def test_success_at_minimum_delay_does_not_record_decrease() -> None:
    policy = RequestPacingPolicy(
        initial_delay_seconds=0.0,
        minimum_delay_seconds=0.0,
        maximum_delay_seconds=2.0,
        failure_increase_seconds=0.25,
        success_decrease_seconds=0.05,
    )
    pacer = AdaptiveRequestPacer(
        policy,
        sleeper=lambda _seconds: None,
    )

    pacer.record_success()

    snapshot = pacer.snapshot

    assert snapshot.current_delay_seconds == 0.0
    assert snapshot.decreases == 0
    assert snapshot.increases == 0


def test_failure_at_maximum_delay_does_not_record_increase() -> None:
    pacer = AdaptiveRequestPacer(
        RequestPacingPolicy(
            initial_delay_seconds=1.0,
            minimum_delay_seconds=0.0,
            maximum_delay_seconds=1.0,
            failure_increase_seconds=0.25,
            success_decrease_seconds=0.05,
        ),
        sleeper=lambda _seconds: None,
    )

    pacer.record_failure()

    snapshot = pacer.snapshot

    assert snapshot.current_delay_seconds == 1.0
    assert snapshot.increases == 0
    assert snapshot.decreases == 0
