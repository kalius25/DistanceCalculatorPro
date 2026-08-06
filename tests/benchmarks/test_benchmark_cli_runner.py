from pathlib import Path
from unittest.mock import MagicMock

import pytest

from app.benchmarks import (
    BenchmarkCliRunner,
    BenchmarkScenario,
    StressBenchmarkResult,
)
from app.models.route_request import RouteRequest

pytestmark = [pytest.mark.benchmark, pytest.mark.benchmark_cli]


def make_result(name: str) -> StressBenchmarkResult:
    return StressBenchmarkResult(
        scenario=name,
        rows=1,
        iterations=1,
        elapsed_seconds=1.0,
        rows_per_second=1.0,
        peak_memory_bytes=1,
        autosave_count=1,
        average_row_latency_seconds=1.0,
        maximum_row_latency_seconds=1.0,
    )


def test_benchmark_cli_runner_executes_and_writes_fixed_artifacts(
    tmp_path: Path,
) -> None:
    benchmark_runner = MagicMock()
    benchmark_runner.run.side_effect = [make_result("smoke"), make_result("1k")]
    runner = BenchmarkCliRunner(benchmark_runner)

    result = runner.run(
        (BenchmarkScenario("smoke", 1), BenchmarkScenario("1k", 1)),
        tmp_path,
    )

    assert [item.scenario for item in result.results] == ["smoke", "1k"]
    assert result.json_path.name == "stress-benchmark.json"
    assert result.markdown_path.name == "stress-benchmark.md"
    assert benchmark_runner.run.call_count == 2


def test_benchmark_cli_runner_rejects_empty_scenarios() -> None:
    with pytest.raises(ValueError, match="At least one"):
        BenchmarkCliRunner().run((), "unused")


def test_benchmark_cli_callbacks_are_deterministic_noops() -> None:
    BenchmarkCliRunner._process_row(RouteRequest("A", "B"))
    BenchmarkCliRunner._autosave(10)
