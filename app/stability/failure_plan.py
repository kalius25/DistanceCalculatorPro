"""Deterministic scheduling of failures by cycle."""

from __future__ import annotations

from dataclasses import dataclass

from .failure_models import FailureEvent


@dataclass(frozen=True, slots=True)
class FailurePlan:
    """Ordered, replayable set of failure events."""

    events: tuple[FailureEvent, ...] = ()

    def __post_init__(self) -> None:
        ordered = tuple(sorted(self.events, key=lambda event: event.cycle))
        object.__setattr__(self, "events", ordered)

    def events_for_cycle(self, cycle: int) -> tuple[FailureEvent, ...]:
        if cycle < 0:
            raise ValueError("Cycle cannot be negative.")
        return tuple(event for event in self.events if event.cycle == cycle)

    def validate_for_cycles(self, cycles: int) -> None:
        if cycles < 1:
            raise ValueError("Recovery cycles must be positive.")
        if any(event.cycle >= cycles for event in self.events):
            raise ValueError("Failure event cycle is outside the scenario range.")


__all__ = ["FailurePlan"]
