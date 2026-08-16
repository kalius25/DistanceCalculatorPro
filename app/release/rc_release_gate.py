"""Guard the Windows RC build against inconsistent v1.3 metadata."""

from __future__ import annotations

import argparse
import tomllib
from pathlib import Path

from app.version import __version__

RC_RUNTIME_VERSION = "1.3.0-rc1"
RC_PACKAGE_VERSION = "1.3.0rc1"


def validate_rc_release(project_root: Path) -> tuple[str, ...]:
    """Return RC metadata problems; empty means the gate passes."""
    issues: list[str] = []

    if __version__ != RC_RUNTIME_VERSION:
        issues.append(
            "Runtime version must be " f"{RC_RUNTIME_VERSION}; found {__version__}."
        )

    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.is_file():
        issues.append(f"Missing package metadata: {pyproject_path}")
        return tuple(issues)

    metadata = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    package_version = metadata.get("project", {}).get("version")
    if package_version != RC_PACKAGE_VERSION:
        issues.append(
            "Package version must be "
            f"{RC_PACKAGE_VERSION}; found {package_version!r}."
        )

    return tuple(issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate DistanceCalculatorPro v1.3 RC metadata."
    )
    parser.add_argument(
        "project_root",
        nargs="?",
        type=Path,
        default=Path.cwd(),
    )
    args = parser.parse_args(argv)

    issues = validate_rc_release(args.project_root)
    if issues:
        print("RC release gate: FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print(f"RC release gate: PASS ({RC_RUNTIME_VERSION})")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
