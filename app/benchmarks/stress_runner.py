"""Large-batch benchmark runner with latency and memory metrics."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from time import perf_counter

from app.models.route_request import RouteRequest

from .memory_sampler import MemorySampler
from .stress_models import BenchmarkScenario, StressBenchmarkResult
from .workload import RouteWorkloadGenerator

Clock = Callable[[], float]
RowWork = Callable[[RouteRequest], None]
AutosaveWork = Callable[[int], None]


class StressBenchmarkRunner:
    """Measure deterministic synthetic route-processing workloads."""

    def __init__(
        self,
        *,
        workload_generator: RouteWorkloadGenerator | None = None,
        memory_sampler: MemorySampler | None = None,
        clock: Clock = perf_counter,
    ) -> None:
        self._workload_generator = workload_generator or RouteWorkloadGenerator()
        self._memory_sampler = memory_sampler or MemorySampler()
        self._clock = clock

    def run(
        self,
        scenario: BenchmarkScenario,
        process_row: RowWork,
        *,
        autosave: AutosaveWork | None = None,
    ) -> StressBenchmarkResult:
        latencies: list[float] = []
        autosaves = 0
        total_rows = scenario.rows * scenario.iterations
        self._memory_sampler.start()
        started = self._clock()
        try:
            for _iteration in range(scenario.iterations):
                rows = self._workload_generator.generate(scenario.rows)
                autosaves += self._run_iteration(
                    rows,
                    process_row,
                    latencies,
                    autosave,
                    scenario.autosave_interval,
                )
            elapsed = max(self._clock() - started, 0.0)
            peak_memory = self._memory_sampler.peak_bytes()
        finally:
            self._memory_sampler.stop()

        average_latency = sum(latencies) / len(latencies)
        maximum_latency = max(latencies)
        throughput = total_rows / elapsed if elapsed > 0 else 0.0
        return StressBenchmarkResult(
            scenario=scenario.name,
            rows=scenario.rows,
            iterations=scenario.iterations,
            elapsed_seconds=elapsed,
            rows_per_second=throughput,
            peak_memory_bytes=peak_memory,
            autosave_count=autosaves,
            average_row_latency_seconds=average_latency,
            maximum_row_latency_seconds=maximum_latency,
        )

    def _run_iteration(
        self,
        rows: Iterable[RouteRequest],
        process_row: RowWork,
        latencies: list[float],
        autosave: AutosaveWork | None,
        autosave_interval: int,
    ) -> int:
        processed = 0
        autosaves = 0
        for processed, request in enumerate(rows, start=1):
            row_started = self._clock()
            process_row(request)
            latencies.append(max(self._clock() - row_started, 0.0))
            if autosave is not None and processed % autosave_interval == 0:
                autosave(processed)
                autosaves += 1
        if autosave is not None and processed % autosave_interval:
            autosave(processed)
            autosaves += 1
        return autosaves


__all__ = ["StressBenchmarkRunner"]
