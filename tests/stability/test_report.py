import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.stability import LeakSnapshot, StabilityReportWriter, StabilityResult

pytestmark = pytest.mark.stability


def result(
    *, violations: tuple[str, ...] = (), handles: int | None = 2
) -> StabilityResult:
    baseline = LeakSnapshot("start", 10, 20, 1, ("main",), (0, 0, 0), 0, handles)
    final = LeakSnapshot("end", 12, 22, 1, ("main",), (0, 0, 0), 0, handles)
    return StabilityResult(
        "smoke",
        2,
        3,
        6,
        baseline,
        final,
        (baseline, final),
        violations,
    )


def test_report_writer_creates_json_and_markdown(tmp_path: Path) -> None:
    json_path, markdown_path = StabilityReportWriter().write(
        result(), tmp_path, stem="report"
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert payload["passed"] is True
    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Status: PASS" in markdown
    assert "Violations: None" in markdown


def test_report_writer_formats_failure_and_unknown_handles(tmp_path: Path) -> None:
    _, markdown_path = StabilityReportWriter().write(
        result(violations=("memory_growth",), handles=None),
        tmp_path,
        stem="failed",
    )

    markdown = markdown_path.read_text(encoding="utf-8")
    assert "Status: FAIL" in markdown
    assert "File-handle growth: Unknown" in markdown
    assert "Violations: memory_growth" in markdown


def test_report_writer_generates_timestamp_stem(tmp_path: Path) -> None:
    with patch("app.stability.report.datetime") as timestamp:
        timestamp.now.return_value.strftime.return_value = "stability-report-fixed"
        json_path, markdown_path = StabilityReportWriter().write(result(), tmp_path)

    assert json_path.name == "stability-report-fixed.json"
    assert markdown_path.name == "stability-report-fixed.md"
