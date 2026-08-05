import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from app.benchmarks import (
    PerformanceGateExitCode,
    PerformanceGateInputError,
    PerformanceGateResult,
    performance_gate,
)
from app.benchmarks.performance_gate import build_parser, main

pytestmark = [pytest.mark.performance_regression, pytest.mark.ci_gate]


def test_parser_requires_paths() -> None:
    args = build_parser().parse_args(
        ["--baseline", "b.json", "--results", "r.json", "--output", "out"]
    )
    assert args.baseline == Path("b.json")


def test_cli_returns_gate_exit_code_and_prints_reports(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    result = PerformanceGateResult((), PerformanceGateExitCode.PASS)
    reports = (tmp_path / "gate.json", tmp_path / "gate.md")
    with (
        patch("app.benchmarks.performance_gate.PerformanceGateRunner") as runner_type,
        patch(
            "app.benchmarks.performance_gate.PerformanceGateReportWriter"
        ) as writer_type,
    ):
        runner_type.return_value.run.return_value = result
        writer_type.return_value.write.return_value = reports
        code = main(
            [
                "--baseline",
                "b.json",
                "--results",
                "r.json",
                "--output",
                str(tmp_path),
                "--fail-on-warning",
            ]
        )

    assert code == 0
    assert "Performance gate PASS" in capsys.readouterr().out
    runner_type.return_value.run.assert_called_once_with(
        Path("b.json"), Path("r.json"), fail_on_warning=True
    )


def test_cli_returns_invalid_input_code(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("app.benchmarks.performance_gate.PerformanceGateRunner") as runner_type:
        runner_type.return_value.run.side_effect = PerformanceGateInputError("bad")
        code = main(["--baseline", "b", "--results", "r", "--output", "out"])

    assert code == 2
    assert "input error: bad" in capsys.readouterr().err


def test_performance_gate_module_entry_point(
    tmp_path: Path,
) -> None:
    baseline_path = tmp_path / "baseline.json"
    results_path = tmp_path / "results.json"
    output_path = tmp_path / "reports"

    baseline_path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "baselines": [
                    {
                        "scenario": "smoke",
                        "elapsed_seconds": 1.0,
                        "rows_per_second": 100.0,
                        "peak_memory_mb": 1.0,
                        "autosave_count": 1,
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    results_path.write_text(
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

    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "app.benchmarks.performance_gate",
            "--baseline",
            str(baseline_path),
            "--results",
            str(results_path),
            "--output",
            str(output_path),
        ],
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode == 0
    assert "Performance gate PASS" in completed.stdout
    assert completed.stderr == ""
    assert (output_path / "performance-gate.json").is_file()
    assert (output_path / "performance-gate.md").is_file()


def test_entry_point_exits_with_main_result() -> None:
    with (
        patch.object(
            performance_gate,
            "main",
            return_value=7,
        ) as main_mock,
        pytest.raises(SystemExit) as raised,
    ):
        performance_gate._entry_point()

    assert raised.value.code == 7
    main_mock.assert_called_once_with()
