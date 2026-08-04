import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.stability import (
    LeakSnapshot,
    RecoveryCycleResult,
    RecoveryReportWriter,
    RecoveryRunResult,
)

pytestmark = [pytest.mark.stability, pytest.mark.failure_injection]


def result() -> RecoveryRunResult:
    snapshot = LeakSnapshot("now", 0, 0, 1, ("Main",), (0, 0, 0), 0, None)
    cycle = RecoveryCycleResult(0, 1, 2, True)
    return RecoveryRunResult("report", 1, 2, snapshot, snapshot, (cycle,))


def test_recovery_report_writes_json_and_markdown(tmp_path: Path) -> None:
    json_path, markdown_path = RecoveryReportWriter().write(
        result(), tmp_path, stem="recovery"
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")
    assert payload["passed"] is True
    assert "# Recovery Stability Report" in markdown
    assert "| 0 | 1 | 2 | Yes | - |" in markdown


def test_recovery_report_builds_timestamped_name(tmp_path: Path) -> None:
    with patch("app.stability.recovery_report.datetime") as timestamp:
        timestamp.now.return_value.strftime.return_value = "recovery-report-fixed"
        paths = RecoveryReportWriter().write(result(), tmp_path)

    assert paths == (
        tmp_path / "recovery-report-fixed.json",
        tmp_path / "recovery-report-fixed.md",
    )
