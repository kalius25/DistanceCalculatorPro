"""Immutable models for deterministic stability and leak checks."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class StabilityScenario:
    """One repeated workload used to evaluate cleanup stability."""

    name: str
    cycles: int
    rows_per_cycle: int
    collect_between_cycles: bool = True

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("Stability scenario name cannot be empty.")
        if self.cycles < 1:
            raise ValueError("Stability cycles must be positive.")
        if self.rows_per_cycle < 1:
            raise ValueError("Rows per cycle must be positive.")


@dataclass(frozen=True, slots=True)
class StabilityPolicy:
    """Maximum allowed resource growth after a stability scenario."""

    max_thread_growth: int = 0
    max_live_reference_growth: int = 0
    max_memory_growth_bytes: int = 8 * 1024 * 1024
    max_file_handle_growth: int = 0

    def __post_init__(self) -> None:
        values = (
            self.max_thread_growth,
            self.max_live_reference_growth,
            self.max_memory_growth_bytes,
            self.max_file_handle_growth,
        )
        if any(value < 0 for value in values):
            raise ValueError("Stability policy limits cannot be negative.")


@dataclass(frozen=True, slots=True)
class LeakSnapshot:
    """One point-in-time view of runtime resources."""

    timestamp: str
    current_memory_bytes: int
    peak_memory_bytes: int
    thread_count: int
    thread_names: tuple[str, ...]
    gc_counts: tuple[int, int, int]
    live_reference_count: int
    file_handle_count: int | None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True, slots=True)
class StabilityResult:
    """Aggregated outcome of one repeated stability scenario."""

    scenario: str
    cycles: int
    rows_per_cycle: int
    total_rows: int
    baseline: LeakSnapshot
    final: LeakSnapshot
    snapshots: tuple[LeakSnapshot, ...]
    violations: tuple[str, ...]

    @property
    def passed(self) -> bool:
        return not self.violations

    @property
    def memory_growth_bytes(self) -> int:
        return self.final.current_memory_bytes - self.baseline.current_memory_bytes

    @property
    def thread_growth(self) -> int:
        return self.final.thread_count - self.baseline.thread_count

    @property
    def live_reference_growth(self) -> int:
        return self.final.live_reference_count - self.baseline.live_reference_count

    @property
    def file_handle_growth(self) -> int | None:
        baseline = self.baseline.file_handle_count
        final = self.final.file_handle_count
        if baseline is None or final is None:
            return None
        return final - baseline

    def to_dict(self) -> dict[str, object]:
        payload: dict[str, object] = asdict(self)
        payload.update(
            {
                "passed": self.passed,
                "memory_growth_bytes": self.memory_growth_bytes,
                "thread_growth": self.thread_growth,
                "live_reference_growth": self.live_reference_growth,
                "file_handle_growth": self.file_handle_growth,
            }
        )
        return payload


__all__ = [
    "LeakSnapshot",
    "StabilityPolicy",
    "StabilityResult",
    "StabilityScenario",
]
