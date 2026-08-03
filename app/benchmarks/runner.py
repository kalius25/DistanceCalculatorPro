"""Synthetic, provider-free benchmark runner for batch infrastructure."""

from __future__ import annotations

from collections.abc import Callable
from time import perf_counter

from .models import BatchBenchmarkResult

Clock = Callable[[], float]
Work = Callable[[int], None]


class BatchBenchmarkRunner:
    """Measure calculation, pacing and autosave phases without real providers."""

    def __init__(self, clock: Clock = perf_counter) -> None:
        self._clock = clock

    def run(
        self,
        job_count: int,
        calculation: Work,
        *,
        pacing: Work | None = None,
        autosave: Work | None = None,
        autosave_interval: int = 20,
    ) -> BatchBenchmarkResult:
        if job_count < 1:
            raise ValueError("Benchmark job count must be positive.")
        if autosave_interval < 1:
            raise ValueError("Autosave interval must be positive.")

        calculation_seconds = 0.0
        autosave_seconds = 0.0
        pacing_seconds = 0.0
        autosaves = 0
        total_started = self._clock()

        for index in range(job_count):
            pacing_seconds += self._measure(pacing, index)
            calculation_seconds += self._measure(calculation, index)
            if autosave is not None and (index + 1) % autosave_interval == 0:
                autosave_seconds += self._measure(autosave, index)
                autosaves += 1

        if autosave is not None and job_count % autosave_interval:
            autosave_seconds += self._measure(autosave, job_count - 1)
            autosaves += 1

        total_seconds = max(self._clock() - total_started, 0.0)
        measured = calculation_seconds + autosave_seconds + pacing_seconds
        overhead = max(total_seconds - measured, 0.0)
        throughput = job_count / total_seconds if total_seconds > 0 else 0.0
        return BatchBenchmarkResult(
            job_count=job_count,
            total_seconds=total_seconds,
            calculation_seconds=calculation_seconds,
            autosave_seconds=autosave_seconds,
            pacing_seconds=pacing_seconds,
            overhead_seconds=overhead,
            jobs_per_second=throughput,
            autosaves=autosaves,
        )

    def _measure(self, work: Work | None, index: int) -> float:
        if work is None:
            return 0.0
        started = self._clock()
        work(index)
        return max(self._clock() - started, 0.0)


__all__ = ["BatchBenchmarkRunner"]
