"""Retry timing policy for recoverable batch failures."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Define maximum attempts and exponential backoff delays."""

    max_attempts: int = 3
    initial_delay_seconds: float = 2.0
    backoff_multiplier: float = 2.0
    max_delay_seconds: float = 30.0

    def __post_init__(self) -> None:
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")
        if self.initial_delay_seconds < 0:
            raise ValueError("initial_delay_seconds cannot be negative")
        if self.backoff_multiplier < 1:
            raise ValueError("backoff_multiplier must be at least 1")
        if self.max_delay_seconds < 0:
            raise ValueError("max_delay_seconds cannot be negative")

    def can_retry(self, attempt_count: int) -> bool:
        """Return whether another attempt is allowed after this attempt."""
        return attempt_count < self.max_attempts

    def delay_for_retry(self, retry_count: int) -> float:
        """Return the delay before a one-based retry number."""
        if retry_count < 1:
            raise ValueError("retry_count must be at least 1")
        delay = self.initial_delay_seconds * (
            self.backoff_multiplier ** (retry_count - 1)
        )
        return min(delay, self.max_delay_seconds)
