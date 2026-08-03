import pytest

from app.engines.performance_models import (
    ProviderPerformanceMetrics,
    ProviderPerformancePolicy,
)


def test_performance_policy_validates_thresholds() -> None:
    policy = ProviderPerformancePolicy(10, 5.0)

    assert policy.page_recycle_interval == 10
    assert policy.slow_request_threshold_seconds == 5.0

    with pytest.raises(ValueError, match="at least one"):
        ProviderPerformancePolicy(page_recycle_interval=0)

    with pytest.raises(ValueError, match="must be positive"):
        ProviderPerformancePolicy(slow_request_threshold_seconds=0.0)


def test_performance_metrics_build_snapshot_and_clamp_duration() -> None:
    metrics = ProviderPerformanceMetrics()

    empty = metrics.snapshot
    assert empty.average_request_seconds == 0.0
    assert empty.maximum_request_seconds == 0.0

    metrics.requests_completed = 1
    metrics.requests_failed = 1
    metrics.record_duration(-5.0)
    metrics.record_duration(4.0)

    snapshot = metrics.snapshot
    assert snapshot.total_request_seconds == 4.0
    assert snapshot.average_request_seconds == 2.0
    assert snapshot.maximum_request_seconds == 4.0
