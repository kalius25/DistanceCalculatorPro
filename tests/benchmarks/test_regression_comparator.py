import pytest

from app.benchmarks import (
    BenchmarkBaseline,
    BenchmarkRegressionComparator,
    RegressionPolicy,
    RegressionStatus,
    StressBenchmarkResult,
)

pytestmark = pytest.mark.performance_regression


def result(
    *,
    scenario: str = "10k",
    elapsed: float = 10.0,
    throughput: float = 1_000.0,
    memory_mb: float = 100.0,
    autosaves: int = 10,
) -> StressBenchmarkResult:
    return StressBenchmarkResult(
        scenario=scenario,
        rows=10_000,
        iterations=1,
        elapsed_seconds=elapsed,
        rows_per_second=throughput,
        peak_memory_bytes=int(memory_mb * 1024 * 1024),
        autosave_count=autosaves,
        average_row_latency_seconds=0.001,
        maximum_row_latency_seconds=0.002,
    )


def baseline() -> BenchmarkBaseline:
    return BenchmarkBaseline("10k", 10.0, 1_000.0, 100.0, 10)


def test_comparator_pass_warning_and_regression() -> None:
    comparator = BenchmarkRegressionComparator()

    passed = comparator.compare(baseline(), result(elapsed=10.5, memory_mb=101))
    warning = comparator.compare(baseline(), result(elapsed=18.0 / 1.6666666667))
    regression = comparator.compare(
        baseline(),
        result(elapsed=12.0, throughput=800.0, memory_mb=120.0, autosaves=11),
    )

    assert comparator.policy == RegressionPolicy()
    assert passed.status is RegressionStatus.PASS
    assert warning.status is RegressionStatus.WARNING
    assert "runtime" in warning.warnings
    assert regression.status is RegressionStatus.REGRESSION
    assert set(regression.regressions) == {
        "runtime",
        "memory",
        "throughput",
        "autosaves",
    }


def test_comparator_handles_improvements_zero_baselines_and_name_mismatch() -> None:
    comparator = BenchmarkRegressionComparator(
        RegressionPolicy(autosave_tolerance=4, warning_fraction=0.5)
    )
    zero = BenchmarkBaseline("zero", 0.0, 0.0, 0.0, 10)

    equal_zero = comparator.compare(
        zero,
        result(scenario="zero", elapsed=0, throughput=0, memory_mb=0, autosaves=12),
    )
    nonzero = comparator.compare(
        zero,
        result(scenario="zero", elapsed=1, throughput=1, memory_mb=1, autosaves=10),
    )
    improved = comparator.compare(
        baseline(),
        result(elapsed=8, throughput=1_200, memory_mb=80, autosaves=10),
    )

    assert equal_zero.status is RegressionStatus.WARNING
    assert equal_zero.autosave_delta == 2
    assert nonzero.status is RegressionStatus.REGRESSION
    assert improved.status is RegressionStatus.PASS

    with pytest.raises(ValueError, match="scenario"):
        comparator.compare(baseline(), result(scenario="other"))


def test_zero_thresholds_regress_on_any_adverse_change_without_warning() -> None:
    comparator = BenchmarkRegressionComparator(
        RegressionPolicy(
            maximum_runtime_regression_percent=0,
            maximum_memory_regression_percent=0,
            maximum_throughput_regression_percent=0,
            autosave_tolerance=0,
        )
    )

    comparison = comparator.compare(
        baseline(),
        result(elapsed=10.1, throughput=999, memory_mb=100.1, autosaves=10),
    )

    assert comparison.status is RegressionStatus.REGRESSION
    assert comparison.warnings == ()
