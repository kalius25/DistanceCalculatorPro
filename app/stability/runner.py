"""Repeated workload runner with deterministic leak-policy evaluation."""

from __future__ import annotations

import gc
from collections.abc import Callable

from .leak_snapshot import LeakSnapshotCollector
from .models import LeakSnapshot, StabilityPolicy, StabilityResult, StabilityScenario

CycleWork = Callable[[int, int], None]
CleanupWork = Callable[[], None]
Collector = Callable[[], int]


class StabilityRunner:
    """Run repeated workloads and compare final resources with a baseline."""

    def __init__(
        self,
        *,
        snapshot_collector: LeakSnapshotCollector | None = None,
        collect_garbage: Collector = gc.collect,
    ) -> None:
        self._snapshot_collector = snapshot_collector or LeakSnapshotCollector()
        self._collect_garbage = collect_garbage

    def run(
        self,
        scenario: StabilityScenario,
        workload: CycleWork,
        *,
        cleanup: CleanupWork | None = None,
        policy: StabilityPolicy | None = None,
    ) -> StabilityResult:
        effective_policy = policy or StabilityPolicy()
        baseline = self._snapshot_collector.capture()
        snapshots = []
        try:
            for cycle in range(scenario.cycles):
                workload(cycle, scenario.rows_per_cycle)
                if cleanup is not None:
                    cleanup()
                if scenario.collect_between_cycles:
                    self._collect_garbage()
                    self._snapshot_collector.tracker.prune()
                snapshots.append(self._snapshot_collector.capture())
        except Exception:
            if cleanup is not None:
                cleanup()
            self._collect_garbage()
            self._snapshot_collector.tracker.prune()
            raise

        if not scenario.collect_between_cycles:
            self._collect_garbage()
            self._snapshot_collector.tracker.prune()
        final = self._snapshot_collector.capture()
        violations = self._evaluate(baseline, final, effective_policy)
        return StabilityResult(
            scenario=scenario.name,
            cycles=scenario.cycles,
            rows_per_cycle=scenario.rows_per_cycle,
            total_rows=scenario.cycles * scenario.rows_per_cycle,
            baseline=baseline,
            final=final,
            snapshots=tuple(snapshots),
            violations=violations,
        )

    @staticmethod
    def _evaluate(
        baseline: LeakSnapshot,
        final: LeakSnapshot,
        policy: StabilityPolicy,
    ) -> tuple[str, ...]:
        violations: list[str] = []
        memory_growth = final.current_memory_bytes - baseline.current_memory_bytes
        thread_growth = final.thread_count - baseline.thread_count
        reference_growth = final.live_reference_count - baseline.live_reference_count

        if memory_growth > policy.max_memory_growth_bytes:
            violations.append("memory_growth")
        if thread_growth > policy.max_thread_growth:
            violations.append("thread_growth")
        if reference_growth > policy.max_live_reference_growth:
            violations.append("live_reference_growth")

        if (
            baseline.file_handle_count is not None
            and final.file_handle_count is not None
        ):
            handle_growth = final.file_handle_count - baseline.file_handle_count
            if handle_growth > policy.max_file_handle_growth:
                violations.append("file_handle_growth")
        return tuple(violations)


__all__ = ["StabilityRunner"]
