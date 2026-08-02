"""Classify existing workbook result values for resumable batches."""

from __future__ import annotations

import re
from dataclasses import dataclass

from .models import RouteJobStatus


@dataclass(frozen=True, slots=True)
class ResumeDecision:
    """Decision derived from one existing result cell."""

    status: RouteJobStatus
    should_skip: bool
    has_result: bool
    distance_km: float | None = None
    reason: str = ""


class ResumeAnalyzer:
    """Determine whether an existing result should be preserved."""

    _DISTANCE_PATTERN = re.compile(
        r"^\s*([+-]?(?:\d+(?:[.,]\d+)?|[.,]\d+))\s*(?:km)?\s*$",
        re.IGNORECASE,
    )
    _ERROR_PREFIXES = ("error:", "failed:", "lỗi:", "loi:")

    def analyze(self, value: object, skip_existing: bool = True) -> ResumeDecision:
        if value is None or not str(value).strip():
            return ResumeDecision(RouteJobStatus.PENDING, False, False, reason="empty")

        text = str(value).strip()
        if text.casefold().startswith(self._ERROR_PREFIXES):
            return ResumeDecision(
                RouteJobStatus.PENDING,
                False,
                True,
                reason="previous_error",
            )

        if not skip_existing:
            return ResumeDecision(
                RouteJobStatus.PENDING,
                False,
                True,
                reason="skip_disabled",
            )

        distance = self._distance(value)
        return ResumeDecision(
            RouteJobStatus.DONE,
            True,
            True,
            distance_km=distance,
            reason="existing_result",
        )

    def _distance(self, value: object) -> float | None:
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return float(value)
        match = self._DISTANCE_PATTERN.fullmatch(str(value))
        if match is None:
            return None
        return float(match.group(1).replace(",", "."))
