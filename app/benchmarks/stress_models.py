"""Models for deterministic large-batch benchmark scenarios."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class BenchmarkScenario:
    """One repeatable benchmark workload."""

    name: str
    rows: int
    iterations: int = 1
    autosave_interval: int = 100

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Benchmark scenario name cannot be empty.")
        if self.rows < 1:
            raise ValueError("Benchmark scenario rows must be positive.")
        if self.iterations < 1:
            raise ValueError("Benchmark iterations must be positive.")
        if self.autosave_interval < 1:
            raise ValueError("Autosave interval must be positive.")


@dataclass(frozen=True, slots=True)
class StressBenchmarkResult:
    """Aggregated performance metrics for one benchmark scenario."""

    scenario: str
    rows: int
    iterations: int
    elapsed_seconds: float
    rows_per_second: float
    peak_memory_bytes: int
    autosave_count: int
    average_row_latency_seconds: float
    maximum_row_latency_seconds: float

    @property
    def peak_memory_mb(self) -> float:
        return self.peak_memory_bytes / (1024 * 1024)

    def to_dict(self) -> dict[str, str | int | float]:
        payload: dict[str, str | int | float] = asdict(self)
        payload["peak_memory_mb"] = self.peak_memory_mb
        return payload


__all__ = ["BenchmarkScenario", "StressBenchmarkResult"]
