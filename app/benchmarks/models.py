"""Models used by synthetic batch performance benchmarks."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class BatchBenchmarkResult:
    """Timing breakdown for one synthetic batch benchmark run."""

    job_count: int
    total_seconds: float
    calculation_seconds: float
    autosave_seconds: float
    pacing_seconds: float
    overhead_seconds: float
    jobs_per_second: float
    autosaves: int

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


__all__ = ["BatchBenchmarkResult"]
