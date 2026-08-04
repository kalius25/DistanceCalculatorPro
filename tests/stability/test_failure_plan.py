import pytest

from app.stability import FailureEvent, FailureKind, FailurePlan

pytestmark = [pytest.mark.stability, pytest.mark.failure_injection]


def test_failure_plan_sorts_and_selects_multiple_events() -> None:
    later = FailureEvent(2, FailureKind.BROWSER_CRASH)
    first = FailureEvent(0, FailureKind.PROVIDER_TIMEOUT)
    second = FailureEvent(0, FailureKind.OUTPUT_LOCKED)
    plan = FailurePlan((later, first, second))

    assert plan.events == (first, second, later)
    assert plan.events_for_cycle(0) == (first, second)
    assert plan.events_for_cycle(1) == ()
    plan.validate_for_cycles(3)


def test_failure_plan_rejects_invalid_cycles() -> None:
    plan = FailurePlan((FailureEvent(2, FailureKind.PARSER_FAILURE),))

    with pytest.raises(ValueError, match="Cycle cannot be negative"):
        plan.events_for_cycle(-1)
    with pytest.raises(ValueError, match="must be positive"):
        plan.validate_for_cycles(0)
    with pytest.raises(ValueError, match="outside"):
        plan.validate_for_cycles(2)
