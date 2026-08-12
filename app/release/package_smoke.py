"""Validate a built DistanceCalculatorPro distribution."""

from __future__ import annotations

import argparse
from pathlib import Path

_REQUIRED_RELATIVE_FILES = (
    Path("app/presentation/styles/light.qss"),
    Path("app/presentation/styles/dark.qss"),
    Path("app/presentation/resources/icons/app_icon.svg"),
    Path("app/presentation/resources/splash.svg"),
    Path("app/browser/chromium/chrome.exe"),
)


def validate_distribution(distribution: Path) -> tuple[str, ...]:
    """Return user-readable packaging problems; empty means PASS."""
    issues: list[str] = []
    executable = distribution / "DistanceCalculatorPro.exe"
    if not executable.is_file():
        issues.append(f"Missing executable: {executable}")

    resource_root = distribution / "_internal"
    for relative_path in _REQUIRED_RELATIVE_FILES:
        resource = resource_root / relative_path
        if not resource.is_file():
            issues.append(f"Missing resource: {resource}")

    return tuple(issues)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate a DistanceCalculatorPro PyInstaller build."
    )
    parser.add_argument(
        "distribution",
        nargs="?",
        type=Path,
        default=Path("dist/DistanceCalculatorPro"),
    )
    args = parser.parse_args(argv)

    issues = validate_distribution(args.distribution)
    if issues:
        print("Packaging smoke: FAIL")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Packaging smoke: PASS")
    print(f"Distribution: {args.distribution.resolve()}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
