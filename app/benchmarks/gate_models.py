"""Models for CI performance regression gate results."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import IntEnum

from .regression_models import RegressionComparison, RegressionStatus


class PerformanceGateExitCode(IntEnum):
    """Process exit codes exposed by the performance gate CLI."""

    PASS = 0
    REGRESSION = 1
    INVALID_INPUT = 2


@dataclass(frozen=True, slots=True)
class PerformanceGateResult:
    """Aggregated outcome for all benchmark comparisons."""

    comparisons: tuple[RegressionComparison, ...]
    exit_code: PerformanceGateExitCode
    fail_on_warning: bool = False

    @property
    def status(self) -> RegressionStatus:
        if any(item.status is RegressionStatus.REGRESSION for item in self.comparisons):
            return RegressionStatus.REGRESSION
        if any(item.status is RegressionStatus.WARNING for item in self.comparisons):
            return RegressionStatus.WARNING
        return RegressionStatus.PASS

    @property
    def passed(self) -> bool:
        return self.exit_code is PerformanceGateExitCode.PASS

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["status"] = self.status.value
        payload["exit_code"] = int(self.exit_code)
        payload["passed"] = self.passed
        payload["comparisons"] = [item.to_dict() for item in self.comparisons]
        return payload


__all__ = ["PerformanceGateExitCode", "PerformanceGateResult"]
