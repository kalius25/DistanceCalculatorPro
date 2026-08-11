"""Launch the packaged GUI briefly and verify clean startup/shutdown."""

from __future__ import annotations

import argparse
import os
import subprocess
from pathlib import Path


def _read_smoke_stage(marker: Path) -> str:
    try:
        value = marker.read_text(encoding="utf-8").strip()
    except OSError:
        return "no startup marker written"
    return value or "empty startup marker"


def run_executable_smoke(
    executable: Path,
    *,
    timeout_seconds: float = 15.0,
    auto_exit_ms: int = 1500,
) -> tuple[bool, str]:
    if not executable.is_file():
        return False, f"Executable not found: {executable}"

    environment = os.environ.copy()
    environment["DCP_EXECUTABLE_SMOKE"] = "1"
    environment["DCP_SMOKE_EXIT_MS"] = str(auto_exit_ms)
    marker = executable.parent / "dcp-smoke-status.txt"
    environment["DCP_SMOKE_STATUS_FILE"] = str(marker)
    marker.unlink(missing_ok=True)

    try:
        completed = subprocess.run(
            [str(executable)],
            env=environment,
            timeout=timeout_seconds,
            check=False,
        )
    except subprocess.TimeoutExpired:
        stage = _read_smoke_stage(marker)
        return False, (
            f"Executable smoke timed out after {timeout_seconds:g} seconds; "
            f"last stage: {stage}"
        )
    except OSError as error:
        return False, f"Unable to launch executable: {error}"

    if completed.returncode != 0:
        return False, (
            "Executable exited with non-zero code " f"{completed.returncode}"
        )

    return True, "Executable startup/shutdown smoke passed"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Launch the packaged DistanceCalculatorPro GUI smoke test."
    )
    parser.add_argument(
        "executable",
        nargs="?",
        type=Path,
        default=Path("dist/DistanceCalculatorPro/DistanceCalculatorPro.exe"),
    )
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--auto-exit-ms", type=int, default=1500)
    args = parser.parse_args(argv)

    passed, message = run_executable_smoke(
        args.executable,
        timeout_seconds=args.timeout,
        auto_exit_ms=args.auto_exit_ms,
    )
    print(f"Executable smoke: {'PASS' if passed else 'FAIL'}")
    print(message)
    return 0 if passed else 1


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
