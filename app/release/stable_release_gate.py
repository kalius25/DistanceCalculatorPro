"""Guard the Windows Stable build against accidental RC metadata."""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

from app.version import __version__

STABLE_VERSION = "1.2.0"


def validate_stable_release(project_root: Path) -> tuple[str, ...]:
    """Return release metadata problems; empty means the Stable gate passes."""
    issues: list[str] = []

    if __version__ != STABLE_VERSION:
        issues.append(
            f"Runtime version must be {STABLE_VERSION}; found {__version__}."
        )

    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        issues.append(f"Missing package metadata: {pyproject_path}")
        return tuple(issues)

    metadata = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    package_version = metadata.get("project", {}).get("version")
    if package_version != STABLE_VERSION:
        issues.append(
            "Package version must be "
            f"{STABLE_VERSION}; found {package_version!r}."
        )

    return tuple(issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate DistanceCalculatorPro Stable metadata."
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        type=Path,
        default=Path.cwd(),
    )
    args = parser.parse_args(argv)

    issues = validate_stable_release(args.project_root)
    if issues:
        print("Stable release gate: FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"Stable release gate: PASS ({STABLE_VERSION})")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
