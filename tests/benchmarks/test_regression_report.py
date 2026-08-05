import json
from pathlib import Path

import pytest

from app.benchmarks import (
    RegressionComparison,
    RegressionReportWriter,
    RegressionStatus,
)

pytestmark = pytest.mark.performance_regression


def comparison(status: RegressionStatus) -> RegressionComparison:
    return RegressionComparison(
        scenario="10k",
        status=status,
        runtime_change_percent=2.5,
        memory_change_percent=-1.0,
        throughput_change_percent=3.0,
        autosave_delta=1,
    )


def test_report_writes_json_and_markdown(tmp_path: Path) -> None:
    writer = RegressionReportWriter()

    json_path, markdown_path = writer.write(
        [comparison(RegressionStatus.WARNING)],
        tmp_path,
        stem="regression",
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert payload["comparisons"][0]["status"] == "WARNING"
    assert "| 10k | WARNING | +2.50% | -1.00% | +3.00% | +1 |" in markdown


def test_report_creates_automatic_unique_stem(tmp_path: Path) -> None:
    json_path, markdown_path = RegressionReportWriter().write([], tmp_path)

    assert json_path.name.startswith("regression-report-")
    assert markdown_path.exists()
