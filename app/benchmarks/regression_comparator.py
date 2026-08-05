"""Compare current benchmark results with approved baselines."""

from __future__ import annotations

from math import ceil

from .regression_models import (
    BenchmarkBaseline,
    RegressionComparison,
    RegressionStatus,
)
from .regression_policy import RegressionPolicy
from .stress_models import StressBenchmarkResult


class BenchmarkRegressionComparator:
    """Classify benchmark changes as pass, warning, or regression."""

    def __init__(self, policy: RegressionPolicy | None = None) -> None:
        self._policy = policy or RegressionPolicy()

    @property
    def policy(self) -> RegressionPolicy:
        return self._policy

    def compare(
        self,
        baseline: BenchmarkBaseline,
        current: StressBenchmarkResult,
    ) -> RegressionComparison:
        if baseline.scenario != current.scenario:
            raise ValueError("Baseline and current scenario names must match.")

        runtime_change = self._percent_change(
            baseline.elapsed_seconds,
            current.elapsed_seconds,
        )
        memory_change = self._percent_change(
            baseline.peak_memory_mb,
            current.peak_memory_mb,
        )
        throughput_change = self._percent_change(
            baseline.rows_per_second,
            current.rows_per_second,
        )
        autosave_delta = current.autosave_count - baseline.autosave_count

        warnings: list[str] = []
        regressions: list[str] = []
        self._classify_percent(
            "runtime",
            runtime_change,
            self._policy.maximum_runtime_regression_percent,
            warnings,
            regressions,
        )
        self._classify_percent(
            "memory",
            memory_change,
            self._policy.maximum_memory_regression_percent,
            warnings,
            regressions,
        )
        self._classify_percent(
            "throughput",
            -throughput_change,
            self._policy.maximum_throughput_regression_percent,
            warnings,
            regressions,
        )
        self._classify_autosaves(
            autosave_delta,
            warnings,
            regressions,
        )

        if regressions:
            status = RegressionStatus.REGRESSION
        elif warnings:
            status = RegressionStatus.WARNING
        else:
            status = RegressionStatus.PASS

        return RegressionComparison(
            scenario=current.scenario,
            status=status,
            runtime_change_percent=runtime_change,
            memory_change_percent=memory_change,
            throughput_change_percent=throughput_change,
            autosave_delta=autosave_delta,
            warnings=tuple(warnings),
            regressions=tuple(regressions),
        )

    @staticmethod
    def _percent_change(baseline: float, current: float) -> float:
        if baseline == 0:
            return 0.0 if current == 0 else 100.0
        return ((current - baseline) / baseline) * 100.0

    def _classify_percent(
        self,
        metric: str,
        adverse_change: float,
        maximum: float,
        warnings: list[str],
        regressions: list[str],
    ) -> None:
        if adverse_change <= 0:
            return
        if adverse_change > maximum:
            regressions.append(metric)
            return
        if maximum > 0 and adverse_change >= maximum * self._policy.warning_fraction:
            warnings.append(metric)

    def _classify_autosaves(
        self,
        delta: int,
        warnings: list[str],
        regressions: list[str],
    ) -> None:
        difference = abs(delta)
        tolerance = self._policy.autosave_tolerance
        if difference > tolerance:
            regressions.append("autosaves")
            return
        if tolerance > 0:
            warning_threshold = max(1, ceil(tolerance * self._policy.warning_fraction))
            if difference >= warning_threshold:
                warnings.append("autosaves")


__all__ = ["BenchmarkRegressionComparator"]
