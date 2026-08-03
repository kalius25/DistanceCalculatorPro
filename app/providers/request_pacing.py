"""Adaptive delay control between web-provider requests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from time import sleep

Sleeper = Callable[[float], None]


@dataclass(frozen=True, slots=True)
class RequestPacingPolicy:
    initial_delay_seconds: float = 0.0
    minimum_delay_seconds: float = 0.0
    maximum_delay_seconds: float = 2.0
    failure_increase_seconds: float = 0.25
    success_decrease_seconds: float = 0.05

    def __post_init__(self) -> None:
        if self.minimum_delay_seconds < 0:
            raise ValueError("Minimum pacing delay cannot be negative.")
        if self.maximum_delay_seconds < self.minimum_delay_seconds:
            raise ValueError("Maximum pacing delay cannot be below minimum.")
        if not (
            self.minimum_delay_seconds
            <= self.initial_delay_seconds
            <= self.maximum_delay_seconds
        ):
            raise ValueError("Initial pacing delay must be within limits.")
        if self.failure_increase_seconds <= 0:
            raise ValueError("Failure pacing increase must be positive.")
        if self.success_decrease_seconds <= 0:
            raise ValueError("Success pacing decrease must be positive.")


@dataclass(frozen=True, slots=True)
class RequestPacingSnapshot:
    waits: int
    total_wait_seconds: float
    current_delay_seconds: float
    increases: int
    decreases: int


class AdaptiveRequestPacer:
    def __init__(
        self,
        policy: RequestPacingPolicy | None = None,
        sleeper: Sleeper = sleep,
    ) -> None:
        self._policy = policy or RequestPacingPolicy()
        self._sleeper = sleeper
        self.reset()

    @property
    def snapshot(self) -> RequestPacingSnapshot:
        return RequestPacingSnapshot(
            waits=self._waits,
            total_wait_seconds=self._total_wait_seconds,
            current_delay_seconds=self._delay,
            increases=self._increases,
            decreases=self._decreases,
        )

    def reset(self) -> None:
        self._delay = self._policy.initial_delay_seconds
        self._waits = 0
        self._total_wait_seconds = 0.0
        self._increases = 0
        self._decreases = 0

    def wait(self) -> None:
        if self._delay <= 0:
            return
        self._sleeper(self._delay)
        self._waits += 1
        self._total_wait_seconds += self._delay

    def record_success(self) -> None:
        updated = max(
            self._policy.minimum_delay_seconds,
            self._delay - self._policy.success_decrease_seconds,
        )
        if updated < self._delay:
            self._decreases += 1
        self._delay = updated

    def record_failure(self) -> None:
        updated = min(
            self._policy.maximum_delay_seconds,
            self._delay + self._policy.failure_increase_seconds,
        )
        if updated > self._delay:
            self._increases += 1
        self._delay = updated


__all__ = [
    "AdaptiveRequestPacer",
    "RequestPacingPolicy",
    "RequestPacingSnapshot",
]
