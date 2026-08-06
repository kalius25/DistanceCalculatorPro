"""Command-line entry point for deterministic stress benchmarks."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .benchmark_cli_models import BenchmarkCliExitCode
from .benchmark_cli_runner import BenchmarkCliRunner
from .stress_models import BenchmarkScenario

_PREDEFINED_ROWS = {
    "smoke": 100,
    "1k": 1_000,
    "5k": 5_000,
    "10k": 10_000,
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deterministic DistanceCalculatorPro stress benchmarks.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/benchmarks"),
    )
    parser.add_argument(
        "--scenario",
        action="append",
        choices=tuple(_PREDEFINED_ROWS),
        help="Run a predefined scenario; may be supplied more than once.",
    )
    parser.add_argument("--rows", type=int)
    parser.add_argument("--iterations", type=int, default=1)
    parser.add_argument("--autosave-interval", type=int, default=100)
    parser.add_argument("--all", action="store_true")
    return parser


def _build_scenarios(args: argparse.Namespace) -> tuple[BenchmarkScenario, ...]:
    if args.all and (args.scenario or args.rows is not None):
        raise ValueError("--all cannot be combined with --scenario or --rows.")
    if args.rows is not None and args.scenario:
        raise ValueError("--rows cannot be combined with --scenario.")

    if args.all:
        names = tuple(_PREDEFINED_ROWS)
    elif args.rows is not None:
        names = ()
    else:
        names = tuple(args.scenario or ("smoke",))

    if args.rows is not None:
        return (
            BenchmarkScenario(
                name=f"custom-{args.rows}",
                rows=args.rows,
                iterations=args.iterations,
                autosave_interval=args.autosave_interval,
            ),
        )

    return tuple(
        BenchmarkScenario(
            name=name,
            rows=_PREDEFINED_ROWS[name],
            iterations=args.iterations,
            autosave_interval=args.autosave_interval,
        )
        for name in names
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        scenarios = _build_scenarios(args)
        result = BenchmarkCliRunner().run(scenarios, args.output)
    except ValueError as error:
        print(f"Benchmark input error: {error}", file=sys.stderr)
        return int(BenchmarkCliExitCode.INVALID_INPUT)
    except Exception as error:
        print(f"Benchmark runtime error: {error}", file=sys.stderr)
        return int(BenchmarkCliExitCode.RUNTIME_ERROR)

    total_rows = sum(item.rows * item.iterations for item in result.results)
    print(
        f"Stress benchmark completed: {len(result.results)} scenario(s), "
        f"{total_rows:,} row(s)."
    )
    print(f"JSON report: {result.json_path}")
    print(f"Markdown report: {result.markdown_path}")
    return int(BenchmarkCliExitCode.SUCCESS)


def _entry_point() -> None:
    raise SystemExit(main())


if __name__ == "__main__":  # pragma: no cover
    _entry_point()


__all__ = ["build_parser", "main"]
