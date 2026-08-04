import pytest

from app.benchmarks import BenchmarkScenario, StressBenchmarkResult

pytestmark = pytest.mark.benchmark


def test_benchmark_scenario_validates_fields() -> None:
    scenario = BenchmarkScenario("10k", 10_000, 2, 500)

    assert scenario.rows == 10_000

    with pytest.raises(ValueError, match="name"):
        BenchmarkScenario(" ", 1)
    with pytest.raises(ValueError, match="rows"):
        BenchmarkScenario("bad", 0)
    with pytest.raises(ValueError, match="iterations"):
        BenchmarkScenario("bad", 1, 0)
    with pytest.raises(ValueError, match="Autosave"):
        BenchmarkScenario("bad", 1, 1, 0)


def test_stress_result_serializes_memory_metrics() -> None:
    result = StressBenchmarkResult(
        scenario="small",
        rows=100,
        iterations=2,
        elapsed_seconds=4.0,
        rows_per_second=50.0,
        peak_memory_bytes=2 * 1024 * 1024,
        autosave_count=4,
        average_row_latency_seconds=0.01,
        maximum_row_latency_seconds=0.02,
    )

    assert result.peak_memory_mb == 2.0
    assert result.to_dict()["peak_memory_mb"] == 2.0
