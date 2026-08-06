"""Models used by the stress benchmark command-line interface."""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

from .stress_models import StressBenchmarkResult


class BenchmarkCliExitCode(IntEnum):
    """Process exit codes returned by the benchmark CLI."""

    SUCCESS = 0
    INVALID_INPUT = 2
    RUNTIME_ERROR = 3


@dataclass(frozen=True, slots=True)
class BenchmarkCliResult:
    """Completed benchmark run and generated report paths."""

    results: tuple[StressBenchmarkResult, ...]
    json_path: Path
    markdown_path: Path


__all__ = ["BenchmarkCliExitCode", "BenchmarkCliResult"]
