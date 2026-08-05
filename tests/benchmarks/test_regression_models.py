import pytest

from app.benchmarks import (
    BenchmarkBaseline,
    RegressionComparison,
    RegressionStatus,
    StressBenchmarkResult,
)

pytestmark = pytest.mark.performance_regression


def make_result() -> StressBenchmarkResult:
    return StressBenchmarkResult(
        scenario="10k",
        rows=10_000,
        iterations=1,
        elapsed_seconds=10.0,
        rows_per_second=1_000.0,
        peak_memory_bytes=20 * 1024 * 1024,
        autosave_count=100,
        average_row_latency_seconds=0.001,
        maximum_row_latency_seconds=0.002,
    )


def test_baseline_validates_serializes_and_builds_from_result() -> None:
    baseline = BenchmarkBaseline.from_result(make_result())

    assert baseline.peak_memory_mb == 20.0
    assert baseline.to_dict()["scenario"] == "10k"

    invalid_values = (
        {
            "scenario": " ",
            "elapsed_seconds": 1,
            "rows_per_second": 1,
            "peak_memory_mb": 1,
            "autosave_count": 1,
        },
        {
            "scenario": "x",
            "elapsed_seconds": -1,
            "rows_per_second": 1,
            "peak_memory_mb": 1,
            "autosave_count": 1,
        },
        {
            "scenario": "x",
            "elapsed_seconds": 1,
            "rows_per_second": -1,
            "peak_memory_mb": 1,
            "autosave_count": 1,
        },
        {
            "scenario": "x",
            "elapsed_seconds": 1,
            "rows_per_second": 1,
            "peak_memory_mb": -1,
            "autosave_count": 1,
        },
        {
            "scenario": "x",
            "elapsed_seconds": 1,
            "rows_per_second": 1,
            "peak_memory_mb": 1,
            "autosave_count": -1,
        },
    )
    for values in invalid_values:
        with pytest.raises(ValueError):
            BenchmarkBaseline(**values)


def test_comparison_serializes_status_and_passed_state() -> None:
    warning = RegressionComparison(
        scenario="10k",
        status=RegressionStatus.WARNING,
        runtime_change_percent=8.0,
        memory_change_percent=0.0,
        throughput_change_percent=-2.0,
        autosave_delta=0,
        warnings=("runtime",),
    )
    regression = RegressionComparison(
        scenario="10k",
        status=RegressionStatus.REGRESSION,
        runtime_change_percent=20.0,
        memory_change_percent=0.0,
        throughput_change_percent=0.0,
        autosave_delta=0,
        regressions=("runtime",),
    )

    assert warning.passed
    assert warning.to_dict()["status"] == "WARNING"
    assert warning.to_dict()["passed"] is True
    assert not regression.passed
