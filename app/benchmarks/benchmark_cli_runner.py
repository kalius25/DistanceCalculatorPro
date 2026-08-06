"""Run stress benchmark scenarios and produce stable CI artifacts."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from app.models.route_request import RouteRequest

from .benchmark_cli_models import BenchmarkCliResult
from .stress_models import BenchmarkScenario
from .stress_report import StressBenchmarkReportWriter
from .stress_runner import StressBenchmarkRunner


class BenchmarkCliRunner:
    """Execute selected scenarios without GUI, browser, or network access."""

    def __init__(
        self,
        benchmark_runner: StressBenchmarkRunner | None = None,
    ) -> None:
        self._benchmark_runner = benchmark_runner or StressBenchmarkRunner()

    def run(
        self,
        scenarios: Iterable[BenchmarkScenario],
        output_directory: str | Path,
    ) -> BenchmarkCliResult:
        selected = tuple(scenarios)
        if not selected:
            raise ValueError("At least one benchmark scenario is required.")

        results = tuple(
            self._benchmark_runner.run(
                scenario,
                self._process_row,
                autosave=self._autosave,
            )
            for scenario in selected
        )
        json_path, markdown_path = StressBenchmarkReportWriter(output_directory).write(
            list(results),
            stem="stress-benchmark",
        )
        return BenchmarkCliResult(results, json_path, markdown_path)

    @staticmethod
    def _process_row(_request: RouteRequest) -> None:
        """Perform deterministic in-process work for one synthetic route."""

    @staticmethod
    def _autosave(_processed_rows: int) -> None:
        """Model the autosave callback without filesystem noise."""


__all__ = ["BenchmarkCliRunner"]
