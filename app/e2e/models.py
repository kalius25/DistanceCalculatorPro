"""Immutable models used by the headless end-to-end reliability harness."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from app.batch.summary import BatchSummary


@dataclass(frozen=True, slots=True)
class E2ERunReport:
    """Serializable outcome of one complete headless batch execution."""

    scenario: str
    source_file: str
    output_file: str
    summary: BatchSummary
    provider_requests: int
    provider_batches_started: int
    provider_batches_finished: int
    statuses: tuple[str, ...]
    report_file: str | None = None

    @property
    def successful(self) -> bool:
        return self.summary.failed == 0 and not self.summary.stopped

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["successful"] = self.successful
        return payload

    def with_report_file(self, path: str | Path) -> E2ERunReport:
        return E2ERunReport(
            scenario=self.scenario,
            source_file=self.source_file,
            output_file=self.output_file,
            summary=self.summary,
            provider_requests=self.provider_requests,
            provider_batches_started=self.provider_batches_started,
            provider_batches_finished=self.provider_batches_finished,
            statuses=self.statuses,
            report_file=str(path),
        )


__all__ = ["E2ERunReport"]
