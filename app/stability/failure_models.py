"""Immutable models for deterministic failure-injection scenarios."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum

from .models import LeakSnapshot


class FailureKind(StrEnum):
    """Supported deterministic failures used by the recovery harness."""

    PROVIDER_TIMEOUT = "provider_timeout"
    PARSER_FAILURE = "parser_failure"
    BROWSER_CRASH = "browser_crash"
    OUTPUT_LOCKED = "output_locked"
    PERMISSION_DENIED = "permission_denied"
    DISK_SPACE_BLOCKED = "disk_space_blocked"
    UNEXPECTED_EXCEPTION = "unexpected_exception"


@dataclass(frozen=True, slots=True)
class FailureEvent:
    """One failure injected before the successful workload attempt of a cycle."""

    cycle: int
    kind: FailureKind
    retryable: bool = True
    label: str = ""

    def __post_init__(self) -> None:
        if self.cycle < 0:
            raise ValueError("Failure cycle cannot be negative.")


@dataclass(frozen=True, slots=True)
class RecoveryEventResult:
    """Outcome of one injected failure and its recovery decision."""

    cycle: int
    kind: FailureKind
    attempt: int
    recovered: bool
    error: str
    action: str

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["kind"] = self.kind.value
        return payload


@dataclass(frozen=True, slots=True)
class RecoveryCycleResult:
    """Aggregated outcome for one cycle in a deterministic recovery run."""

    cycle: int
    attempts: int
    completed_rows: int
    recovered: bool
    events: tuple[RecoveryEventResult, ...] = ()
    error: str = ""

    @property
    def passed(self) -> bool:
        return self.recovered and not self.error

    def to_dict(self) -> dict[str, object]:
        return {
            "cycle": self.cycle,
            "attempts": self.attempts,
            "completed_rows": self.completed_rows,
            "recovered": self.recovered,
            "passed": self.passed,
            "events": [event.to_dict() for event in self.events],
            "error": self.error,
        }


@dataclass(frozen=True, slots=True)
class RecoveryRunResult:
    """Final result of a deterministic failure and recovery scenario."""

    scenario: str
    cycles: int
    rows_per_cycle: int
    baseline: LeakSnapshot
    final: LeakSnapshot
    cycle_results: tuple[RecoveryCycleResult, ...]
    violations: tuple[str, ...] = ()

    @property
    def recovered_failures(self) -> int:
        return sum(
            event.recovered for cycle in self.cycle_results for event in cycle.events
        )

    @property
    def unrecovered_failures(self) -> int:
        return sum(
            not event.recovered
            for cycle in self.cycle_results
            for event in cycle.events
        )

    @property
    def completed_rows(self) -> int:
        return sum(cycle.completed_rows for cycle in self.cycle_results)

    @property
    def passed(self) -> bool:
        return (
            not self.violations
            and self.unrecovered_failures == 0
            and all(cycle.passed for cycle in self.cycle_results)
        )

    def to_dict(self) -> dict[str, object]:
        return {
            "scenario": self.scenario,
            "cycles": self.cycles,
            "rows_per_cycle": self.rows_per_cycle,
            "completed_rows": self.completed_rows,
            "recovered_failures": self.recovered_failures,
            "unrecovered_failures": self.unrecovered_failures,
            "passed": self.passed,
            "violations": list(self.violations),
            "baseline": self.baseline.to_dict(),
            "final": self.final.to_dict(),
            "cycle_results": [cycle.to_dict() for cycle in self.cycle_results],
        }


__all__ = [
    "FailureEvent",
    "FailureKind",
    "RecoveryCycleResult",
    "RecoveryEventResult",
    "RecoveryRunResult",
]
