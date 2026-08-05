import json
from pathlib import Path

import pytest

from app.benchmarks import (
    PerformanceGateExitCode,
    PerformanceGateReportWriter,
    PerformanceGateResult,
    RegressionComparison,
    RegressionStatus,
)

pytestmark = [pytest.mark.performance_regression, pytest.mark.ci_gate]


def test_gate_report_writes_json_and_markdown(tmp_path: Path) -> None:
    result = PerformanceGateResult(
        (RegressionComparison("10k", RegressionStatus.PASS, 1, 2, 3, 0),),
        PerformanceGateExitCode.PASS,
    )

    json_path, markdown_path = PerformanceGateReportWriter().write(result, tmp_path)

    assert json.loads(json_path.read_text())["status"] == "PASS"
    assert "| 10k | PASS |" in markdown_path.read_text()
