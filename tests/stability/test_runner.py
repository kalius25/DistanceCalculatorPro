from collections.abc import Iterator
from unittest.mock import MagicMock

import pytest

from app.stability import (
    LeakSnapshot,
    LeakSnapshotCollector,
    StabilityPolicy,
    StabilityRunner,
    StabilityScenario,
)

pytestmark = pytest.mark.stability


class SnapshotSequence:
    def __init__(self, values: list[LeakSnapshot]) -> None:
        self._values: Iterator[LeakSnapshot] = iter(values)

    def __call__(self) -> LeakSnapshot:
        return next(self._values)


def snapshot(
    memory: int,
    *,
    threads: int = 1,
    references: int = 0,
    handles: int | None = 2,
) -> LeakSnapshot:
    return LeakSnapshot(
        timestamp=str(memory),
        current_memory_bytes=memory,
        peak_memory_bytes=memory,
        thread_count=threads,
        thread_names=("main",),
        gc_counts=(0, 0, 0),
        live_reference_count=references,
        file_handle_count=handles,
    )


def collector(values: list[LeakSnapshot]) -> LeakSnapshotCollector:
    result = LeakSnapshotCollector()
    result.capture = SnapshotSequence(values)  # type: ignore[method-assign]
    return result


def test_runner_executes_cycles_collects_and_passes_policy() -> None:
    snapshots = [snapshot(10), snapshot(11), snapshot(12), snapshot(13)]
    collect = MagicMock(return_value=0)
    cleanup = MagicMock()
    workload = MagicMock()
    runner = StabilityRunner(
        snapshot_collector=collector(snapshots),
        collect_garbage=collect,
    )

    result = runner.run(
        StabilityScenario("smoke", cycles=2, rows_per_cycle=5),
        workload,
        cleanup=cleanup,
        policy=StabilityPolicy(max_memory_growth_bytes=10),
    )

    assert result.passed
    assert result.total_rows == 10
    assert len(result.snapshots) == 2
    assert workload.call_args_list[0].args == (0, 5)
    assert workload.call_args_list[1].args == (1, 5)
    assert cleanup.call_count == 2
    assert collect.call_count == 2


def test_runner_collects_once_at_end_when_cycle_collection_disabled() -> None:
    collect = MagicMock(return_value=0)
    runner = StabilityRunner(
        snapshot_collector=collector([snapshot(1), snapshot(2), snapshot(3)]),
        collect_garbage=collect,
    )

    result = runner.run(
        StabilityScenario("deferred", 1, 1, collect_between_cycles=False),
        lambda _cycle, _rows: None,
    )

    assert result.passed
    collect.assert_called_once_with()


def test_runner_reports_all_policy_violations() -> None:
    runner = StabilityRunner(
        snapshot_collector=collector(
            [
                snapshot(10, handles=1),
                snapshot(20, threads=3, references=2, handles=4),
                snapshot(20, threads=3, references=2, handles=4),
            ]
        )
    )

    result = runner.run(
        StabilityScenario("leaky", 1, 1),
        lambda _cycle, _rows: None,
        policy=StabilityPolicy(max_memory_growth_bytes=0),
    )

    assert result.violations == (
        "memory_growth",
        "thread_growth",
        "live_reference_growth",
        "file_handle_growth",
    )


def test_runner_ignores_file_handles_when_unavailable() -> None:
    runner = StabilityRunner(
        snapshot_collector=collector(
            [snapshot(1, handles=None), snapshot(1, handles=3), snapshot(1, handles=3)]
        )
    )

    result = runner.run(
        StabilityScenario("unknown", 1, 1),
        lambda _cycle, _rows: None,
    )

    assert result.passed


def test_runner_cleans_up_and_reraises_workload_errors() -> None:
    cleanup = MagicMock()
    collect = MagicMock(return_value=0)
    tracker = MagicMock()
    snapshot_collector = MagicMock()
    snapshot_collector.capture.return_value = snapshot(1)
    snapshot_collector.tracker = tracker
    runner = StabilityRunner(
        snapshot_collector=snapshot_collector,
        collect_garbage=collect,
    )

    with pytest.raises(RuntimeError, match="failed"):
        runner.run(
            StabilityScenario("error", 1, 1),
            MagicMock(side_effect=RuntimeError("failed")),
            cleanup=cleanup,
        )

    cleanup.assert_called_once_with()
    collect.assert_called_once_with()
    tracker.prune.assert_called_once_with()


def test_runner_reraises_without_optional_cleanup() -> None:
    collect = MagicMock(return_value=0)
    tracker = MagicMock()
    snapshot_collector = MagicMock()
    snapshot_collector.capture.return_value = snapshot(1)
    snapshot_collector.tracker = tracker
    runner = StabilityRunner(
        snapshot_collector=snapshot_collector,
        collect_garbage=collect,
    )

    with pytest.raises(RuntimeError, match="failed"):
        runner.run(
            StabilityScenario("error-without-cleanup", 1, 1),
            MagicMock(side_effect=RuntimeError("failed")),
        )

    collect.assert_called_once_with()
    tracker.prune.assert_called_once_with()
