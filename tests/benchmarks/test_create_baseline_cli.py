import json
from pathlib import Path
from unittest.mock import patch

import pytest

from app.benchmarks import create_baseline

pytestmark = pytest.mark.baseline_management


def result_file(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "scenario": "smoke",
                        "rows": 100,
                        "iterations": 1,
                        "elapsed_seconds": 1.0,
                        "rows_per_second": 100.0,
                        "peak_memory_bytes": 1_048_576,
                        "autosave_count": 1,
                        "average_row_latency_seconds": 0.01,
                        "maximum_row_latency_seconds": 0.02,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_cli_create_merge_replace_dry_run_and_error(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    results = tmp_path / "results.json"
    output = tmp_path / "baseline.json"
    reports = tmp_path / "reports"
    result_file(results)

    assert (
        create_baseline.main(
            [
                "--results",
                str(results),
                "--output",
                str(output),
                "--report-output",
                str(reports),
            ]
        )
        == 0
    )
    assert "Baseline update completed" in capsys.readouterr().out

    assert (
        create_baseline.main(
            [
                "--results",
                str(results),
                "--output",
                str(output),
                "--merge",
                "--dry-run",
                "--scenario",
                "smoke",
            ]
        )
        == 0
    )
    assert (
        create_baseline.main(
            [
                "--results",
                str(results),
                "--output",
                str(output),
                "--replace",
            ]
        )
        == 0
    )
    assert (
        create_baseline.main(
            [
                "--results",
                str(tmp_path / "missing.json"),
                "--output",
                str(output),
            ]
        )
        == 2
    )
    assert "input error" in capsys.readouterr().err


def test_cli_write_error_and_entry_point(tmp_path: Path) -> None:
    results = tmp_path / "results.json"
    result_file(results)
    with patch(
        "app.benchmarks.create_baseline.BaselineUpdateReportWriter.write",
        side_effect=OSError("locked"),
    ):
        assert (
            create_baseline.main(
                [
                    "--results",
                    str(results),
                    "--output",
                    str(tmp_path / "baseline.json"),
                ]
            )
            == 3
        )

    with (
        patch.object(create_baseline, "main", return_value=7),
        pytest.raises(SystemExit) as raised,
    ):
        create_baseline._entry_point()
    assert raised.value.code == 7


def test_cli_can_ignore_missing_scenarios(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    results = tmp_path / "results.json"
    output = tmp_path / "baseline.json"
    result_file(results)

    assert (
        create_baseline.main(
            [
                "--results",
                str(results),
                "--output",
                str(output),
                "--scenario",
                "missing",
                "--scenario",
                "smoke",
                "--ignore-missing-scenarios",
            ]
        )
        == 0
    )

    captured = capsys.readouterr()
    assert "Ignored missing scenarios: missing" in captured.out
    assert captured.err == ""


def test_cli_reports_all_missing_scenarios(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    results = tmp_path / "results.json"
    output = tmp_path / "baseline.json"
    result_file(results)

    assert (
        create_baseline.main(
            [
                "--results",
                str(results),
                "--output",
                str(output),
                "--scenario",
                "missing",
                "--ignore-missing-scenarios",
            ]
        )
        == 2
    )

    captured = capsys.readouterr()
    assert "No requested benchmark scenarios were found" in captured.err
    assert "Available scenarios" in captured.err
    assert "smoke" in captured.err
