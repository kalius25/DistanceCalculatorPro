"""Stage Playwright Chromium for the PyInstaller distribution."""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from app.engines.browser_executable import playwright_browser_executable


def stage_browser(destination: Path) -> Path:
    """Copy Chromium beside build inputs and return staged executable."""
    executable = playwright_browser_executable()
    if not executable.is_file():
        raise FileNotFoundError(
            f"Playwright Chromium executable is missing: {executable}"
        )

    source_directory = executable.parent
    if destination.exists():
        shutil.rmtree(destination)

    shutil.copytree(source_directory, destination)
    staged_executable = destination / executable.name
    if not staged_executable.is_file():
        raise FileNotFoundError(
            f"Staged Chromium executable is missing: {staged_executable}"
        )
    return staged_executable


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Stage Playwright Chromium for packaging."
    )
    parser.add_argument(
        "destination",
        nargs="?",
        type=Path,
        default=Path("build/bundled-browser/chromium"),
    )
    args = parser.parse_args(argv)

    staged = stage_browser(args.destination)
    print(f"Bundled Chromium staged: {staged.resolve()}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
