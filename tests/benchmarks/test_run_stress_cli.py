from pathlib import Path
from unittest.mock import patch

import pytest

from app.benchmarks import BenchmarkCliExitCode, BenchmarkCliResult, run_stress

pytestmark = [pytest.mark.benchmark, pytest.mark.benchmark_cli]


def test_parser_and_default_smoke_scenario() -> None:
    args = run_stress.build_parser().parse_args([])
    scenarios = run_stress._build_scenarios(args)

    assert args.output == Path("artifacts/benchmarks")
    assert [(item.name, item.rows) for item in scenarios] == [("smoke", 100)]


def test_builds_all_predefined_scenarios() -> None:
    args = run_stress.build_parser().parse_args(
        ["--all", "--iterations", "2", "--autosave-interval", "50"]
    )

    scenarios = run_stress._build_scenarios(args)

    assert [item.name for item in scenarios] == ["smoke", "1k", "5k", "10k"]
    assert all(item.iterations == 2 for item in scenarios)
    assert all(item.autosave_interval == 50 for item in scenarios)


def test_builds_selected_and_custom_scenarios() -> None:
    selected = run_stress._build_scenarios(
        run_stress.build_parser().parse_args(["--scenario", "1k", "--scenario", "5k"])
    )
    custom = run_stress._build_scenarios(
        run_stress.build_parser().parse_args(["--rows", "25", "--iterations", "3"])
    )

    assert [item.name for item in selected] == ["1k", "5k"]
    assert custom[0].name == "custom-25"
    assert custom[0].iterations == 3


@pytest.mark.parametrize(
    "arguments, message",
    [
        (["--all", "--rows", "10"], "--all cannot"),
        (["--rows", "10", "--scenario", "smoke"], "--rows cannot"),
        (["--rows", "0"], "rows must be positive"),
        (["--iterations", "0"], "iterations must be positive"),
        (["--autosave-interval", "0"], "Autosave interval"),
    ],
)
def test_main_rejects_invalid_configuration(
    arguments: list[str],
    message: str,
    capsys: pytest.CaptureFixture[str],
) -> None:
    assert run_stress.main(arguments) == int(BenchmarkCliExitCode.INVALID_INPUT)
    assert message in capsys.readouterr().err


def test_main_runs_benchmark_and_prints_artifacts(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    result = BenchmarkCliResult(
        (),
        tmp_path / "stress-benchmark.json",
        tmp_path / "stress-benchmark.md",
    )
    with patch("app.benchmarks.run_stress.BenchmarkCliRunner") as runner_type:
        runner_type.return_value.run.return_value = result
        code = run_stress.main(["--output", str(tmp_path)])

    assert code == int(BenchmarkCliExitCode.SUCCESS)
    assert "Stress benchmark completed" in capsys.readouterr().out
    runner_type.return_value.run.assert_called_once()


def test_main_reports_runtime_failure(capsys: pytest.CaptureFixture[str]) -> None:
    with patch("app.benchmarks.run_stress.BenchmarkCliRunner") as runner_type:
        runner_type.return_value.run.side_effect = RuntimeError("boom")
        code = run_stress.main([])

    assert code == int(BenchmarkCliExitCode.RUNTIME_ERROR)
    assert "runtime error: boom" in capsys.readouterr().err


def test_entry_point_exits_with_main_result() -> None:
    with (
        patch.object(run_stress, "main", return_value=3) as main_mock,
        pytest.raises(SystemExit) as raised,
    ):
        run_stress._entry_point()

    assert raised.value.code == 3
    main_mock.assert_called_once_with()
