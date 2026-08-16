from pathlib import Path
from subprocess import CompletedProcess, TimeoutExpired
from unittest.mock import patch

from app.release.executable_smoke import main, run_executable_smoke


def test_executable_smoke_reports_missing_executable(
    tmp_path: Path,
) -> None:
    executable = tmp_path / "missing.exe"

    passed, message = run_executable_smoke(executable)

    assert not passed
    assert message == f"Executable not found: {executable}"


def test_executable_smoke_passes_clean_exit(tmp_path: Path) -> None:
    executable = tmp_path / "DistanceCalculatorPro.exe"
    executable.write_bytes(b"exe")

    with patch(
        "app.release.executable_smoke.subprocess.run",
        return_value=CompletedProcess([str(executable)], 0),
    ) as run:
        passed, message = run_executable_smoke(
            executable,
            timeout_seconds=8,
            auto_exit_ms=900,
        )

    assert passed
    assert message == "Executable startup/shutdown smoke passed"
    environment = run.call_args.kwargs["env"]
    assert environment["DCP_SMOKE_EXIT_MS"] == "900"
    assert run.call_args.kwargs["timeout"] == 8
    assert run.call_args.kwargs["check"] is False


def test_executable_smoke_reports_nonzero_exit(tmp_path: Path) -> None:
    executable = tmp_path / "DistanceCalculatorPro.exe"
    executable.write_bytes(b"exe")

    with patch(
        "app.release.executable_smoke.subprocess.run",
        return_value=CompletedProcess([str(executable)], 3),
    ):
        passed, message = run_executable_smoke(executable)

    assert not passed
    assert message == "Executable exited with non-zero code 3"


def test_executable_smoke_reports_timeout(tmp_path: Path) -> None:
    executable = tmp_path / "DistanceCalculatorPro.exe"
    executable.write_bytes(b"exe")

    with patch(
        "app.release.executable_smoke.subprocess.run",
        side_effect=TimeoutExpired(str(executable), 4),
    ):
        passed, message = run_executable_smoke(
            executable,
            timeout_seconds=4,
        )

    assert not passed
    assert message == (
        "Executable smoke timed out after 4 seconds; "
        "last stage: no startup marker written"
    )


def test_executable_smoke_reports_launch_error(tmp_path: Path) -> None:
    executable = tmp_path / "DistanceCalculatorPro.exe"
    executable.write_bytes(b"exe")

    with patch(
        "app.release.executable_smoke.subprocess.run",
        side_effect=OSError("blocked"),
    ):
        passed, message = run_executable_smoke(executable)

    assert not passed
    assert message == "Unable to launch executable: blocked"


def test_executable_smoke_main_reports_pass(
    tmp_path: Path,
    capsys,
) -> None:
    executable = tmp_path / "DistanceCalculatorPro.exe"
    executable.write_bytes(b"exe")

    with patch(
        "app.release.executable_smoke.run_executable_smoke",
        return_value=(True, "ok"),
    ):
        result = main([str(executable)])

    assert result == 0
    assert "Executable smoke: PASS" in capsys.readouterr().out


def test_executable_smoke_main_reports_fail(
    tmp_path: Path,
    capsys,
) -> None:
    executable = tmp_path / "DistanceCalculatorPro.exe"

    with patch(
        "app.release.executable_smoke.run_executable_smoke",
        return_value=(False, "failed"),
    ):
        result = main([str(executable)])

    assert result == 1
    assert "Executable smoke: FAIL" in capsys.readouterr().out



def test_read_smoke_stage_reads_marker(tmp_path: Path) -> None:
    from app.release.executable_smoke import _read_smoke_stage

    marker = tmp_path / "status.txt"
    marker.write_text("before event loop", encoding="utf-8")

    assert _read_smoke_stage(marker) == "before event loop"


def test_read_smoke_stage_reports_empty_marker(tmp_path: Path) -> None:
    from app.release.executable_smoke import _read_smoke_stage

    marker = tmp_path / "status.txt"
    marker.write_text("", encoding="utf-8")

    assert _read_smoke_stage(marker) == "empty startup marker"
