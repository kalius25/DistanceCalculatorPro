"""Command-line entry point for benchmark baseline management."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .baseline_update_models import BaselineUpdateMode
from .baseline_update_report import BaselineUpdateReportWriter
from .baseline_update_runner import BaselineUpdateInputError, BaselineUpdateRunner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Create or update an approved benchmark baseline.",
    )
    parser.add_argument("--results", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--merge", action="store_true")
    mode.add_argument("--replace", action="store_true")
    parser.add_argument("--scenario", action="append", default=[])
    parser.add_argument(
        "--ignore-missing-scenarios",
        action="store_true",
        help=(
            "Ignore requested scenarios absent from the benchmark results, "
            "provided at least one requested scenario is available."
        ),
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--report-output", type=Path)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    mode = (
        BaselineUpdateMode.MERGE
        if args.merge
        else BaselineUpdateMode.REPLACE if args.replace else BaselineUpdateMode.CREATE
    )
    try:
        result = BaselineUpdateRunner().run(
            args.results,
            args.output,
            mode=mode,
            scenarios=tuple(args.scenario),
            dry_run=args.dry_run,
            ignore_missing_scenarios=args.ignore_missing_scenarios,
        )
        report_directory = args.report_output or args.output.parent
        json_path, markdown_path = BaselineUpdateReportWriter().write(
            result,
            report_directory,
        )
    except BaselineUpdateInputError as error:
        print(f"Baseline update input error: {error}", file=sys.stderr)
        return 2
    except OSError as error:
        print(f"Baseline update write error: {error}", file=sys.stderr)
        return 3

    verb = "previewed" if result.dry_run else "completed"
    print(f"Baseline update {verb}: {result.mode.value}.")
    print(
        f"Added: {len(result.added)}, updated: {len(result.updated)}, "
        f"retained: {len(result.retained)}, removed: {len(result.removed)}."
    )
    if result.missing_scenarios:
        print("Ignored missing scenarios: " + ", ".join(result.missing_scenarios))
    print(f"JSON report: {json_path}")
    print(f"Markdown report: {markdown_path}")
    return 0


def _entry_point() -> None:
    raise SystemExit(main())


if __name__ == "__main__":  # pragma: no cover
    _entry_point()


__all__ = ["build_parser", "main"]
