from unittest.mock import MagicMock

import pytest

from app.stability import (
    FailureEvent,
    FailureKind,
    FailurePlan,
    LeakSnapshot,
    RecoveryRunner,
    StabilityPolicy,
    StabilityScenario,
)

pytestmark = [pytest.mark.stability, pytest.mark.failure_injection]


def make_snapshot(
    memory: int = 0,
    threads: int = 1,
    references: int = 0,
    handles: int | None = 1,
) -> LeakSnapshot:
    return LeakSnapshot(
        "now",
        memory,
        memory,
        threads,
        tuple(f"T{index}" for index in range(threads)),
        (0, 0, 0),
        references,
        handles,
    )


def test_recovery_runner_recovers_failures_and_continues_cycles() -> None:
    collector = MagicMock()
    collector.capture.side_effect = [make_snapshot(), make_snapshot()]
    collector.tracker = MagicMock()
    garbage = MagicMock(return_value=0)
    cleanup = MagicMock()
    runner = RecoveryRunner(snapshot_collector=collector, collect_garbage=garbage)
    plan = FailurePlan(
        (
            FailureEvent(0, FailureKind.PROVIDER_TIMEOUT),
            FailureEvent(0, FailureKind.OUTPUT_LOCKED),
        )
    )
    calls: list[tuple[int, FailureKind | None, int]] = []

    def execute(cycle: int, rows: int, event: FailureEvent | None, attempt: int) -> int:
        calls.append((cycle, event.kind if event else None, attempt))
        if event is not None:
            raise RuntimeError(event.kind.value)
        return rows

    recover = MagicMock(return_value=True)
    result = runner.run(
        StabilityScenario("recover", 2, 5),
        plan,
        execute,
        recover=recover,
        cleanup=cleanup,
    )

    assert result.passed
    assert result.completed_rows == 10
    assert result.recovered_failures == 2
    assert calls[-1] == (1, None, 1)
    assert cleanup.call_count == 2
    assert garbage.call_count == 2
    assert collector.tracker.prune.call_count == 2


def test_recovery_runner_keeps_later_cycles_after_unrecovered_failure() -> None:
    collector = MagicMock()
    collector.capture.side_effect = [make_snapshot(), make_snapshot()]
    collector.tracker = MagicMock()
    runner = RecoveryRunner(snapshot_collector=collector, collect_garbage=lambda: 0)
    event = FailureEvent(0, FailureKind.PARSER_FAILURE, retryable=False)
    completed_cycles: list[int] = []

    def execute(
        cycle: int,
        rows: int,
        injected: FailureEvent | None,
        _attempt: int,
    ) -> int:
        if injected is not None:
            raise ValueError("bad parser")
        completed_cycles.append(cycle)
        return rows

    recover = MagicMock(return_value=True)
    result = runner.run(
        StabilityScenario("continue", 2, 3),
        FailurePlan((event,)),
        execute,
        recover=recover,
    )

    assert not result.passed
    assert result.unrecovered_failures == 1
    assert completed_cycles == [1]
    recover.assert_not_called()


def test_recovery_runner_cleans_up_and_reraises_unexpected_executor_error() -> None:
    collector = MagicMock()
    collector.capture.return_value = make_snapshot()
    collector.tracker = MagicMock()
    cleanup = MagicMock()
    garbage = MagicMock(return_value=0)
    runner = RecoveryRunner(snapshot_collector=collector, collect_garbage=garbage)

    with pytest.raises(RuntimeError, match="unexpected"):
        runner.run(
            StabilityScenario("boom", 1, 1),
            FailurePlan(),
            lambda *_args: (_ for _ in ()).throw(RuntimeError("unexpected")),
            recover=lambda _event, _error: False,
            cleanup=cleanup,
        )

    cleanup.assert_called_once_with()
    garbage.assert_called_once_with()
    collector.tracker.prune.assert_called_once_with()


def test_recovery_runner_collects_once_at_end_and_reports_all_violations() -> None:
    collector = MagicMock()
    collector.capture.side_effect = [
        make_snapshot(0, 1, 0, 1),
        make_snapshot(9 * 1024 * 1024, 3, 2, 4),
    ]
    collector.tracker = MagicMock()
    garbage = MagicMock(return_value=0)
    runner = RecoveryRunner(snapshot_collector=collector, collect_garbage=garbage)

    result = runner.run(
        StabilityScenario("growth", 1, 1, collect_between_cycles=False),
        FailurePlan(),
        lambda _cycle, rows, _event, _attempt: rows,
        recover=lambda _event, _error: False,
        policy=StabilityPolicy(),
    )

    assert result.violations == (
        "memory_growth",
        "thread_growth",
        "live_reference_growth",
        "file_handle_growth",
    )
    garbage.assert_called_once_with()


def test_recovery_runner_ignores_unknown_file_handle_growth() -> None:
    collector = MagicMock()
    collector.capture.side_effect = [
        make_snapshot(handles=None),
        make_snapshot(handles=5),
    ]
    collector.tracker = MagicMock()
    runner = RecoveryRunner(snapshot_collector=collector, collect_garbage=lambda: 0)

    result = runner.run(
        StabilityScenario("handles", 1, 1),
        FailurePlan(),
        lambda _cycle, rows, _event, _attempt: rows,
        recover=lambda _event, _error: False,
    )

    assert result.passed
