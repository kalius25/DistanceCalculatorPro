import json
from pathlib import Path

import pytest

from app.benchmarks import (
    BenchmarkBaseline,
    BenchmarkBaselineStore,
    PerformanceGateExitCode,
    PerformanceGateInputError,
    PerformanceGateRunner,
    RegressionPolicy,
)
from app.benchmarks.regression_comparator import BenchmarkRegressionComparator

pytestmark = [pytest.mark.performance_regression, pytest.mark.ci_gate]


def write_results(
    path: Path, *, elapsed: float = 10.0, duplicate: bool = False
) -> None:
    row = {
        "scenario": "10k",
        "rows": 10_000,
        "iterations": 1,
        "elapsed_seconds": elapsed,
        "rows_per_second": 1_000.0,
        "peak_memory_bytes": 10 * 1024 * 1024,
        "autosave_count": 100,
        "average_row_latency_seconds": 0.001,
        "maximum_row_latency_seconds": 0.002,
    }
    path.write_text(json.dumps({"results": [row, row] if duplicate else [row]}))


def baseline(path: Path) -> None:
    BenchmarkBaselineStore().save(
        path,
        [BenchmarkBaseline("10k", 10.0, 1_000.0, 10.0, 100)],
    )


def test_gate_runner_pass_warning_and_fail_on_warning(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.json"
    results_path = tmp_path / "results.json"
    baseline(baseline_path)
    write_results(results_path, elapsed=10.8)
    comparator = BenchmarkRegressionComparator(
        RegressionPolicy(maximum_runtime_regression_percent=10.0)
    )
    runner = PerformanceGateRunner(comparator=comparator)

    normal = runner.run(baseline_path, results_path)
    strict = runner.run(baseline_path, results_path, fail_on_warning=True)

    assert normal.exit_code is PerformanceGateExitCode.PASS
    assert strict.exit_code is PerformanceGateExitCode.REGRESSION


def test_gate_runner_detects_regression(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.json"
    results_path = tmp_path / "results.json"
    baseline(baseline_path)
    write_results(results_path, elapsed=12.0)

    result = PerformanceGateRunner().run(baseline_path, results_path)

    assert result.exit_code is PerformanceGateExitCode.REGRESSION


def test_gate_runner_rejects_empty_baseline(tmp_path: Path) -> None:
    results_path = tmp_path / "results.json"
    write_results(results_path)

    with pytest.raises(PerformanceGateInputError, match="empty"):
        PerformanceGateRunner().run(tmp_path / "missing.json", results_path)


@pytest.mark.parametrize(
    "content, message",
    [
        ("not-json", "invalid"),
        (json.dumps({"results": []}), "empty"),
    ],
)
def test_gate_runner_rejects_invalid_result_file(
    tmp_path: Path,
    content: str,
    message: str,
) -> None:
    baseline_path = tmp_path / "baseline.json"
    results_path = tmp_path / "results.json"
    baseline(baseline_path)
    results_path.write_text(content)

    with pytest.raises(PerformanceGateInputError, match=message):
        PerformanceGateRunner().run(baseline_path, results_path)


def test_gate_runner_rejects_duplicate_results(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.json"
    results_path = tmp_path / "results.json"
    baseline(baseline_path)
    write_results(results_path, duplicate=True)

    with pytest.raises(PerformanceGateInputError, match="Duplicate"):
        PerformanceGateRunner().run(baseline_path, results_path)


def test_gate_runner_rejects_missing_baseline_scenario(tmp_path: Path) -> None:
    baseline_path = tmp_path / "baseline.json"
    results_path = tmp_path / "results.json"
    BenchmarkBaselineStore().save(
        baseline_path,
        [BenchmarkBaseline("5k", 5.0, 1_000.0, 5.0, 50)],
    )
    write_results(results_path)

    with pytest.raises(PerformanceGateInputError, match="not found"):
        PerformanceGateRunner().run(baseline_path, results_path)


def test_gate_runner_rejects_missing_results_file(
    tmp_path: Path,
) -> None:
    baseline_path = tmp_path / "baseline.json"
    results_path = tmp_path / "missing-results.json"

    BenchmarkBaselineStore().save(
        baseline_path,
        (
            BenchmarkBaseline(
                scenario="smoke",
                elapsed_seconds=1.0,
                rows_per_second=100.0,
                peak_memory_mb=1.0,
                autosave_count=1,
            ),
        ),
    )

    with pytest.raises(
        PerformanceGateInputError,
        match="Benchmark results not found",
    ):
        PerformanceGateRunner().run(
            baseline_path,
            results_path,
        )


def test_gate_runner_rejects_invalid_results_collection(
    tmp_path: Path,
) -> None:
    baseline_path = tmp_path / "baseline.json"
    results_path = tmp_path / "results.json"

    BenchmarkBaselineStore().save(
        baseline_path,
        (
            BenchmarkBaseline(
                scenario="smoke",
                elapsed_seconds=1.0,
                rows_per_second=100.0,
                peak_memory_mb=1.0,
                autosave_count=1,
            ),
        ),
    )

    results_path.write_text(
        json.dumps(
            {
                "results": {
                    "scenario": "smoke",
                }
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(
        PerformanceGateInputError,
        match="Benchmark result list is invalid",
    ):
        PerformanceGateRunner().run(
            baseline_path,
            results_path,
        )
