"""Threshold policy for benchmark regression detection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class RegressionPolicy:
    """Allowed performance movement before warning or regression."""

    maximum_runtime_regression_percent: float = 10.0
    maximum_memory_regression_percent: float = 15.0
    maximum_throughput_regression_percent: float = 10.0
    autosave_tolerance: int = 0
    warning_fraction: float = 0.75

    def __post_init__(self) -> None:
        percentages = (
            self.maximum_runtime_regression_percent,
            self.maximum_memory_regression_percent,
            self.maximum_throughput_regression_percent,
        )
        if any(value < 0 for value in percentages):
            raise ValueError("Regression percentages cannot be negative.")
        if self.autosave_tolerance < 0:
            raise ValueError("Autosave tolerance cannot be negative.")
        if not 0.0 < self.warning_fraction <= 1.0:
            raise ValueError("warning_fraction must be greater than 0 and at most 1.")


__all__ = ["RegressionPolicy"]
