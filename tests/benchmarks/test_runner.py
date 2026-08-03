from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.benchmarks import (
    BatchBenchmarkResult,
    BatchBenchmarkRunner,
    BenchmarkReportWriter,
)


class Clock:
    def __init__(self, values: list[float]) -> None:
        self._values = iter(values)

    def __call__(self) -> float:
        return next(self._values)


def test_benchmark_runner_measures_all_phases_and_final_autosave() -> None:
    calls: list[tuple[str, int]] = []
    value = -0.1

    def clock() -> float:
        nonlocal value
        value += 0.1
        return value

    runner = BatchBenchmarkRunner(clock)

    result = runner.run(
        3,
        lambda index: calls.append(("calculation", index)),
        pacing=lambda index: calls.append(("pacing", index)),
        autosave=lambda index: calls.append(("autosave", index)),
        autosave_interval=2,
    )

    assert result.job_count == 3
    assert result.calculation_seconds == pytest.approx(0.3)
    assert result.pacing_seconds == pytest.approx(0.3)
    assert result.autosave_seconds == pytest.approx(0.2)
    assert result.total_seconds == pytest.approx(1.7)
    assert result.overhead_seconds == pytest.approx(0.9)
    assert result.jobs_per_second == pytest.approx(3 / 1.7)
    assert result.autosaves == 2
    assert calls[-1] == ("autosave", 2)


def test_benchmark_runner_handles_optional_phases_and_zero_duration() -> None:
    runner = BatchBenchmarkRunner(Clock([1.0, 1.0, 1.0, 1.0]))

    result = runner.run(1, lambda _index: None)

    assert result.total_seconds == 0.0
    assert result.jobs_per_second == 0.0
    assert result.autosaves == 0
    assert result.overhead_seconds == 0.0


def test_benchmark_runner_rejects_invalid_configuration() -> None:
    runner = BatchBenchmarkRunner()
    with pytest.raises(ValueError, match="job count"):
        runner.run(0, lambda _index: None)
    with pytest.raises(ValueError, match="Autosave interval"):
        runner.run(1, lambda _index: None, autosave_interval=0)


def test_benchmark_result_to_dict_and_report_writer(tmp_path: Path) -> None:
    result = BatchBenchmarkResult(
        job_count=100,
        total_seconds=10.0,
        calculation_seconds=7.0,
        autosave_seconds=1.0,
        pacing_seconds=1.0,
        overhead_seconds=1.0,
        jobs_per_second=10.0,
        autosaves=5,
    )

    assert result.to_dict()["job_count"] == 100
    path = BenchmarkReportWriter(tmp_path).write([result])
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert path.parent == tmp_path
    assert payload["created_at"]
    assert payload["results"][0]["jobs_per_second"] == 10.0
