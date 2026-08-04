import pytest

from app.stability import (
    LeakSnapshot,
    StabilityPolicy,
    StabilityResult,
    StabilityScenario,
)

pytestmark = pytest.mark.stability


def snapshot(
    *,
    memory: int = 10,
    threads: int = 1,
    references: int = 0,
    handles: int | None = 2,
) -> LeakSnapshot:
    return LeakSnapshot(
        timestamp="2026-08-04T00:00:00+00:00",
        current_memory_bytes=memory,
        peak_memory_bytes=memory + 5,
        thread_count=threads,
        thread_names=("MainThread",),
        gc_counts=(1, 2, 3),
        live_reference_count=references,
        file_handle_count=handles,
    )


def test_scenario_and_policy_validate_inputs() -> None:
    with pytest.raises(ValueError, match="name"):
        StabilityScenario(" ", 1, 1)
    with pytest.raises(ValueError, match="cycles"):
        StabilityScenario("test", 0, 1)
    with pytest.raises(ValueError, match="Rows"):
        StabilityScenario("test", 1, 0)
    with pytest.raises(ValueError, match="negative"):
        StabilityPolicy(max_thread_growth=-1)


def test_result_properties_and_serialization() -> None:
    baseline = snapshot()
    final = snapshot(memory=14, threads=2, references=1, handles=4)
    result = StabilityResult(
        scenario="smoke",
        cycles=2,
        rows_per_cycle=3,
        total_rows=6,
        baseline=baseline,
        final=final,
        snapshots=(baseline, final),
        violations=("thread_growth",),
    )

    assert not result.passed
    assert result.memory_growth_bytes == 4
    assert result.thread_growth == 1
    assert result.live_reference_growth == 1
    assert result.file_handle_growth == 2
    assert baseline.to_dict()["timestamp"] == baseline.timestamp
    payload = result.to_dict()
    assert payload["passed"] is False
    assert payload["memory_growth_bytes"] == 4


def test_result_handles_unknown_file_handle_growth() -> None:
    result = StabilityResult(
        scenario="unknown-handles",
        cycles=1,
        rows_per_cycle=1,
        total_rows=1,
        baseline=snapshot(handles=None),
        final=snapshot(handles=4),
        snapshots=(),
        violations=(),
    )

    assert result.passed
    assert result.file_handle_growth is None
