"""Immutable models for benchmark regression comparisons."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum

from .stress_models import StressBenchmarkResult


class RegressionStatus(StrEnum):
    """Severity assigned to one benchmark comparison."""

    PASS = "PASS"
    WARNING = "WARNING"
    REGRESSION = "REGRESSION"


@dataclass(frozen=True, slots=True)
class BenchmarkBaseline:
    """Approved performance metrics for one benchmark scenario."""

    scenario: str
    elapsed_seconds: float
    rows_per_second: float
    peak_memory_mb: float
    autosave_count: int

    def __post_init__(self) -> None:
        if not self.scenario.strip():
            raise ValueError("Baseline scenario cannot be empty.")
        if self.elapsed_seconds < 0:
            raise ValueError("Baseline elapsed_seconds cannot be negative.")
        if self.rows_per_second < 0:
            raise ValueError("Baseline rows_per_second cannot be negative.")
        if self.peak_memory_mb < 0:
            raise ValueError("Baseline peak_memory_mb cannot be negative.")
        if self.autosave_count < 0:
            raise ValueError("Baseline autosave_count cannot be negative.")

    @classmethod
    def from_result(cls, result: StressBenchmarkResult) -> BenchmarkBaseline:
        """Create an approved baseline from a benchmark result."""

        return cls(
            scenario=result.scenario,
            elapsed_seconds=result.elapsed_seconds,
            rows_per_second=result.rows_per_second,
            peak_memory_mb=result.peak_memory_mb,
            autosave_count=result.autosave_count,
        )

    def to_dict(self) -> dict[str, str | int | float]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class RegressionComparison:
    """Difference between approved and current performance metrics."""

    scenario: str
    status: RegressionStatus
    runtime_change_percent: float
    memory_change_percent: float
    throughput_change_percent: float
    autosave_delta: int
    warnings: tuple[str, ...] = ()
    regressions: tuple[str, ...] = ()

    @property
    def passed(self) -> bool:
        return self.status is not RegressionStatus.REGRESSION

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["passed"] = self.passed
        return payload


__all__ = [
    "BenchmarkBaseline",
    "RegressionComparison",
    "RegressionStatus",
]
