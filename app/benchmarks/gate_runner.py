"""Run benchmark comparisons as a deterministic CI gate."""

from __future__ import annotations

import json
from pathlib import Path

from .baseline_store import BenchmarkBaselineStore
from .gate_models import PerformanceGateExitCode, PerformanceGateResult
from .regression_comparator import BenchmarkRegressionComparator
from .regression_models import RegressionStatus
from .stress_models import StressBenchmarkResult


class PerformanceGateInputError(ValueError):
    """Raised when baseline or current benchmark input is invalid."""


class PerformanceGateRunner:
    """Load benchmark artifacts and aggregate regression comparisons."""

    def __init__(
        self,
        baseline_store: BenchmarkBaselineStore | None = None,
        comparator: BenchmarkRegressionComparator | None = None,
    ) -> None:
        self._baseline_store = baseline_store or BenchmarkBaselineStore()
        self._comparator = comparator or BenchmarkRegressionComparator()

    def run(
        self,
        baseline_path: str | Path,
        results_path: str | Path,
        *,
        fail_on_warning: bool = False,
    ) -> PerformanceGateResult:
        try:
            baselines = self._baseline_store.load(baseline_path)
            if not baselines:
                raise PerformanceGateInputError("Benchmark baseline is empty.")
            results = self._load_results(results_path)
            if not results:
                raise PerformanceGateInputError("Benchmark results are empty.")
            comparisons = tuple(
                self._comparator.compare(
                    self._baseline_store.find(baselines, result.scenario),
                    result,
                )
                for result in results
            )
        except (KeyError, OSError, ValueError, TypeError) as error:
            if isinstance(error, PerformanceGateInputError):
                raise
            raise PerformanceGateInputError(str(error)) from error

        has_regression = any(
            item.status is RegressionStatus.REGRESSION for item in comparisons
        )
        has_warning = any(
            item.status is RegressionStatus.WARNING for item in comparisons
        )
        failed = has_regression or (fail_on_warning and has_warning)
        exit_code = (
            PerformanceGateExitCode.REGRESSION
            if failed
            else PerformanceGateExitCode.PASS
        )
        return PerformanceGateResult(
            comparisons=comparisons,
            exit_code=exit_code,
            fail_on_warning=fail_on_warning,
        )

    @staticmethod
    def _load_results(path: str | Path) -> tuple[StressBenchmarkResult, ...]:
        source = Path(path)
        if not source.exists():
            raise PerformanceGateInputError(f"Benchmark results not found: {source}")
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
            raw_results = payload.get("results")
            if not isinstance(raw_results, list):
                raise PerformanceGateInputError("Benchmark result list is invalid.")
            results = tuple(
                StressBenchmarkResult(
                    scenario=item["scenario"],
                    rows=item["rows"],
                    iterations=item["iterations"],
                    elapsed_seconds=item["elapsed_seconds"],
                    rows_per_second=item["rows_per_second"],
                    peak_memory_bytes=item["peak_memory_bytes"],
                    autosave_count=item["autosave_count"],
                    average_row_latency_seconds=item["average_row_latency_seconds"],
                    maximum_row_latency_seconds=item["maximum_row_latency_seconds"],
                )
                for item in raw_results
            )
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as error:
            raise PerformanceGateInputError(
                "Benchmark result file is invalid."
            ) from error
        scenarios = [item.scenario for item in results]
        if len(scenarios) != len(set(scenarios)):
            raise PerformanceGateInputError("Duplicate benchmark result scenario.")
        return results


__all__ = ["PerformanceGateInputError", "PerformanceGateRunner"]
