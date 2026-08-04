from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest

from app.benchmarks import BenchmarkScenario, StressBenchmarkRunner
from app.models.route_request import RouteRequest

pytestmark = pytest.mark.benchmark


class Clock:
    def __init__(self, values: list[float]) -> None:
        self._values: Iterator[float] = iter(values)

    def __call__(self) -> float:
        return next(self._values)


def test_stress_runner_measures_rows_autosaves_and_memory() -> None:
    sampler = MagicMock()
    sampler.peak_bytes.return_value = 3_145_728
    processed: list[str] = []
    saved: list[int] = []
    runner = StressBenchmarkRunner(
        memory_sampler=sampler,
        clock=Clock([0.0, 0.0, 0.1, 0.1, 0.3, 0.3, 0.6, 1.0]),
    )

    result = runner.run(
        BenchmarkScenario("three", 3, autosave_interval=2),
        lambda request: processed.append(request.origin),
        autosave=saved.append,
    )

    assert processed == ["Origin 0", "Origin 1", "Origin 2"]
    assert saved == [2, 3]
    assert result.elapsed_seconds == pytest.approx(1.0)
    assert result.rows_per_second == pytest.approx(3.0)
    assert result.average_row_latency_seconds == pytest.approx(0.2)
    assert result.maximum_row_latency_seconds == pytest.approx(0.3)
    assert result.autosave_count == 2
    assert result.peak_memory_bytes == 3_145_728
    sampler.start.assert_called_once_with()
    sampler.stop.assert_called_once_with()


def test_stress_runner_supports_iterations_without_autosave_and_zero_elapsed() -> None:
    runner = StressBenchmarkRunner(
        clock=Clock([0.0, 0.0, 0.0, 0.0, 0.0, 0.0]),
    )

    result = runner.run(
        BenchmarkScenario("repeat", 1, iterations=2),
        lambda _request: None,
    )

    assert result.rows_per_second == 0.0
    assert result.autosave_count == 0
    assert result.iterations == 2


def test_stress_runner_stops_memory_sampler_when_processing_fails() -> None:
    sampler = MagicMock()
    runner = StressBenchmarkRunner(
        memory_sampler=sampler,
        clock=Clock([0.0, 0.0]),
    )

    def fail(_request: RouteRequest) -> None:
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError, match="boom"):
        runner.run(BenchmarkScenario("failure", 1), fail)

    sampler.stop.assert_called_once_with()
