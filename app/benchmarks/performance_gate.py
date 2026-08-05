"""Command-line entry point for the benchmark performance gate."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .gate_models import PerformanceGateExitCode
from .gate_report import PerformanceGateReportWriter
from .gate_runner import PerformanceGateInputError, PerformanceGateRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Compare benchmark results with an approved baseline.",
    )
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--fail-on-warning", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        result = PerformanceGateRunner().run(
            args.baseline,
            args.results,
            fail_on_warning=args.fail_on_warning,
        )
        json_path, markdown_path = PerformanceGateReportWriter().write(
            result,
            args.output,
        )
    except PerformanceGateInputError as error:
        print(f"Performance gate input error: {error}", file=sys.stderr)
        return int(PerformanceGateExitCode.INVALID_INPUT)

    print(
        f"Performance gate {result.status.value}: "
        f"{len(result.comparisons)} scenario(s)."
    )
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    return int(result.exit_code)


def _entry_point() -> None:
    raise SystemExit(main())


if __name__ == "__main__":  # pragma: no cover
    _entry_point()


__all__ = [
    "build_parser",
    "main",
]
