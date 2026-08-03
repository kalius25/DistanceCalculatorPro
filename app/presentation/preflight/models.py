"""Immutable models for batch resource preflight checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PreflightPolicy:
    """Thresholds used to estimate and protect large batch execution."""

    large_batch_job_count: int = 10_000
    estimated_bytes_per_job: int = 2_048
    output_size_multiplier: float = 1.25
    minimum_reserved_bytes: int = 64 * 1024 * 1024

    def __post_init__(self) -> None:
        if self.large_batch_job_count < 1:
            raise ValueError("large_batch_job_count must be at least 1")
        if self.estimated_bytes_per_job < 1:
            raise ValueError("estimated_bytes_per_job must be at least 1")
        if self.output_size_multiplier < 1.0:
            raise ValueError("output_size_multiplier must be at least 1.0")
        if self.minimum_reserved_bytes < 0:
            raise ValueError("minimum_reserved_bytes cannot be negative")


@dataclass(frozen=True, slots=True)
class PreflightIssue:
    """One actionable warning or blocking preflight problem."""

    code: str
    title: str
    message: str
    blocking: bool


@dataclass(frozen=True, slots=True)
class PreflightResult:
    """Combined batch preflight outcome."""

    output_path: Path
    estimated_job_count: int
    estimated_output_bytes: int
    required_free_bytes: int
    available_bytes: int | None
    issues: tuple[PreflightIssue, ...] = ()

    @property
    def ok(self) -> bool:
        return not any(issue.blocking for issue in self.issues)

    @property
    def blocking_issues(self) -> tuple[PreflightIssue, ...]:
        return tuple(issue for issue in self.issues if issue.blocking)

    @property
    def warnings(self) -> tuple[PreflightIssue, ...]:
        return tuple(issue for issue in self.issues if not issue.blocking)


__all__ = ["PreflightIssue", "PreflightPolicy", "PreflightResult"]
