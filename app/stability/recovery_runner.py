"""Deterministic failure-injection runner with cleanup and leak checks."""

from __future__ import annotations

import gc
from collections.abc import Callable

from .failure_models import (
    FailureEvent,
    RecoveryCycleResult,
    RecoveryEventResult,
    RecoveryRunResult,
)
from .failure_plan import FailurePlan
from .leak_snapshot import LeakSnapshotCollector
from .models import LeakSnapshot, StabilityPolicy, StabilityScenario

CycleExecutor = Callable[[int, int, FailureEvent | None, int], int]
RecoveryHandler = Callable[[FailureEvent, Exception], bool]
CleanupWork = Callable[[], None]
Collector = Callable[[], int]


class RecoveryRunner:
    """Replay scheduled failures and verify later cycles remain healthy."""

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
        plan: FailurePlan,
        executor: CycleExecutor,
        *,
        recover: RecoveryHandler,
        cleanup: CleanupWork | None = None,
        policy: StabilityPolicy | None = None,
    ) -> RecoveryRunResult:
        plan.validate_for_cycles(scenario.cycles)
        effective_policy = policy or StabilityPolicy()
        baseline = self._snapshot_collector.capture()
        cycle_results: list[RecoveryCycleResult] = []

        try:
            for cycle in range(scenario.cycles):
                cycle_results.append(
                    self._run_cycle(
                        cycle,
                        scenario.rows_per_cycle,
                        plan.events_for_cycle(cycle),
                        executor,
                        recover,
                    )
                )
                self._cleanup_cycle(cleanup, scenario.collect_between_cycles)
        except Exception:
            self._cleanup_cycle(cleanup, True)
            raise

        if not scenario.collect_between_cycles:
            self._cleanup_cycle(cleanup, True)
        final = self._snapshot_collector.capture()
        violations = self._evaluate(baseline, final, effective_policy)
        return RecoveryRunResult(
            scenario=scenario.name,
            cycles=scenario.cycles,
            rows_per_cycle=scenario.rows_per_cycle,
            baseline=baseline,
            final=final,
            cycle_results=tuple(cycle_results),
            violations=violations,
        )

    def _run_cycle(
        self,
        cycle: int,
        rows: int,
        events: tuple[FailureEvent, ...],
        executor: CycleExecutor,
        recover: RecoveryHandler,
    ) -> RecoveryCycleResult:
        attempts = 0
        event_results: list[RecoveryEventResult] = []
        for event in events:
            attempts += 1
            try:
                executor(cycle, rows, event, attempts)
            except Exception as error:
                recovered = event.retryable and recover(event, error)
                event_results.append(
                    RecoveryEventResult(
                        cycle=cycle,
                        kind=event.kind,
                        attempt=attempts,
                        recovered=recovered,
                        error=str(error),
                        action="retry" if recovered else "abort_cycle",
                    )
                )
                if not recovered:
                    return RecoveryCycleResult(
                        cycle=cycle,
                        attempts=attempts,
                        completed_rows=0,
                        recovered=False,
                        events=tuple(event_results),
                        error=str(error),
                    )

        attempts += 1
        completed_rows = executor(cycle, rows, None, attempts)
        return RecoveryCycleResult(
            cycle=cycle,
            attempts=attempts,
            completed_rows=max(int(completed_rows), 0),
            recovered=True,
            events=tuple(event_results),
        )

    def _cleanup_cycle(
        self,
        cleanup: CleanupWork | None,
        collect: bool,
    ) -> None:
        if cleanup is not None:
            cleanup()
        if collect:
            self._collect_garbage()
            self._snapshot_collector.tracker.prune()

    @staticmethod
    def _evaluate(
        baseline: LeakSnapshot,
        final: LeakSnapshot,
        policy: StabilityPolicy,
    ) -> tuple[str, ...]:
        violations: list[str] = []
        if (
            final.current_memory_bytes - baseline.current_memory_bytes
            > policy.max_memory_growth_bytes
        ):
            violations.append("memory_growth")
        if final.thread_count - baseline.thread_count > policy.max_thread_growth:
            violations.append("thread_growth")
        if (
            final.live_reference_count - baseline.live_reference_count
            > policy.max_live_reference_growth
        ):
            violations.append("live_reference_growth")
        if (
            baseline.file_handle_count is not None
            and final.file_handle_count is not None
        ):
            if (
                final.file_handle_count - baseline.file_handle_count
                > policy.max_file_handle_growth
            ):
                violations.append("file_handle_growth")
        return tuple(violations)


__all__ = ["RecoveryRunner"]
