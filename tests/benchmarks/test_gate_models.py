import pytest

from app.benchmarks import (
    PerformanceGateExitCode,
    PerformanceGateResult,
    RegressionComparison,
    RegressionStatus,
)

pytestmark = [pytest.mark.performance_regression, pytest.mark.ci_gate]


def comparison(status: RegressionStatus) -> RegressionComparison:
    return RegressionComparison("10k", status, 1.0, 2.0, -1.0, 0)


def test_gate_result_aggregates_status_and_serializes() -> None:
    passed = PerformanceGateResult((), PerformanceGateExitCode.PASS)
    warning = PerformanceGateResult(
        (comparison(RegressionStatus.WARNING),),
        PerformanceGateExitCode.PASS,
    )
    regression = PerformanceGateResult(
        (
            comparison(RegressionStatus.WARNING),
            comparison(RegressionStatus.REGRESSION),
        ),
        PerformanceGateExitCode.REGRESSION,
        True,
    )

    assert passed.status is RegressionStatus.PASS
    assert passed.passed
    assert warning.status is RegressionStatus.WARNING
    assert regression.status is RegressionStatus.REGRESSION
    assert not regression.passed
    assert regression.to_dict()["exit_code"] == 1
