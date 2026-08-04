"""JSON and Markdown reports for stability scenarios."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .models import StabilityResult


class StabilityReportWriter:
    """Persist one stability result in machine- and human-readable formats."""

    def write(
        self,
        result: StabilityResult,
        directory: str | Path,
        *,
        stem: str | None = None,
    ) -> tuple[Path, Path]:
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        resolved_stem = stem or datetime.now(UTC).strftime(
            "stability-report-%Y%m%d-%H%M%S"
        )
        json_path = target / f"{resolved_stem}.json"
        markdown_path = target / f"{resolved_stem}.md"
        json_path.write_text(
            json.dumps(result.to_dict(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        markdown_path.write_text(self._markdown(result), encoding="utf-8")
        return json_path, markdown_path

    @staticmethod
    def _markdown(result: StabilityResult) -> str:
        status = "PASS" if result.passed else "FAIL"
        violations = ", ".join(result.violations) or "None"
        handles = (
            "Unknown"
            if result.file_handle_growth is None
            else str(result.file_handle_growth)
        )
        return (
            "# Stability Report\n\n"
            f"- Scenario: {result.scenario}\n"
            f"- Status: {status}\n"
            f"- Cycles: {result.cycles}\n"
            f"- Rows per cycle: {result.rows_per_cycle}\n"
            f"- Total rows: {result.total_rows}\n"
            f"- Memory growth: {result.memory_growth_bytes} bytes\n"
            f"- Thread growth: {result.thread_growth}\n"
            f"- Live-reference growth: {result.live_reference_growth}\n"
            f"- File-handle growth: {handles}\n"
            f"- Violations: {violations}\n"
        )


__all__ = ["StabilityReportWriter"]
