import pytest

from app.batch import RetryPolicy


def test_retry_policy_calculates_exponential_delays_and_caps_maximum() -> None:
    policy = RetryPolicy(
        max_attempts=5,
        initial_delay_seconds=2.0,
        backoff_multiplier=2.0,
        max_delay_seconds=5.0,
    )

    assert policy.can_retry(0)
    assert policy.can_retry(4)
    assert not policy.can_retry(5)
    assert policy.delay_for_retry(1) == 2.0
    assert policy.delay_for_retry(2) == 4.0
    assert policy.delay_for_retry(3) == 5.0


def test_retry_policy_rejects_invalid_configuration_and_retry_number() -> None:
    with pytest.raises(ValueError, match="max_attempts"):
        RetryPolicy(max_attempts=0)
    with pytest.raises(ValueError, match="initial_delay_seconds"):
        RetryPolicy(initial_delay_seconds=-1)
    with pytest.raises(ValueError, match="backoff_multiplier"):
        RetryPolicy(backoff_multiplier=0.5)
    with pytest.raises(ValueError, match="max_delay_seconds"):
        RetryPolicy(max_delay_seconds=-1)

    policy = RetryPolicy()
    with pytest.raises(ValueError, match="retry_count"):
        policy.delay_for_retry(0)
