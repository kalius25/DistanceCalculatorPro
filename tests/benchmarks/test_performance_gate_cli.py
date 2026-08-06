from pathlib import Path
from unittest.mock import patch

import pytest

from app.benchmarks import (
    PerformanceGateExitCode,
    PerformanceGateInputError,
    PerformanceGateResult,
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


def test_entry_point_exits_with_main_result() -> None:
    from app.benchmarks import performance_gate

    with (
        patch.object(performance_gate, "main", return_value=7) as main_mock,
        pytest.raises(SystemExit) as raised,
    ):
        performance_gate._entry_point()

    assert raised.value.code == 7
    main_mock.assert_called_once_with()
