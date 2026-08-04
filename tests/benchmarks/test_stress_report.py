import json
from pathlib import Path

import pytest

from app.benchmarks import StressBenchmarkReportWriter, StressBenchmarkResult

pytestmark = pytest.mark.benchmark


def make_result() -> StressBenchmarkResult:
    return StressBenchmarkResult(
        scenario="1k",
        rows=1_000,
        iterations=1,
        elapsed_seconds=2.0,
        rows_per_second=500.0,
        peak_memory_bytes=1_048_576,
        autosave_count=10,
        average_row_latency_seconds=0.002,
        maximum_row_latency_seconds=0.01,
    )


def test_stress_report_writes_json_and_markdown(tmp_path: Path) -> None:
    json_path, markdown_path = StressBenchmarkReportWriter(tmp_path).write(
        [make_result()],
        stem="baseline",
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert payload["results"][0]["scenario"] == "1k"
    assert "| 1k | 1,000 | 1 | 2.000 | 500.00 | 1.00 | 10 |" in markdown


def test_stress_report_generates_timestamped_name(tmp_path: Path) -> None:
    json_path, markdown_path = StressBenchmarkReportWriter(tmp_path).write([])

    assert json_path.name.startswith("stress-benchmark-")
    assert markdown_path.stem == json_path.stem
    assert StressBenchmarkReportWriter._render_markdown([]).endswith("\n")
