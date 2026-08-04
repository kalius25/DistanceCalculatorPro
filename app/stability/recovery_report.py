"""JSON and Markdown reports for deterministic recovery runs."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .failure_models import RecoveryRunResult


class RecoveryReportWriter:
    """Persist recovery results for automated and human inspection."""

    def write(
        self,
        result: RecoveryRunResult,
        directory: str | Path,
        *,
        stem: str | None = None,
    ) -> tuple[Path, Path]:
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        resolved_stem = stem or datetime.now(UTC).strftime(
            "recovery-report-%Y%m%d-%H%M%S"
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
    def _markdown(result: RecoveryRunResult) -> str:
        status = "PASS" if result.passed else "FAIL"
        lines = [
            "# Recovery Stability Report",
            "",
            f"- Scenario: {result.scenario}",
            f"- Status: {status}",
            f"- Cycles: {result.cycles}",
            f"- Completed rows: {result.completed_rows}",
            f"- Recovered failures: {result.recovered_failures}",
            f"- Unrecovered failures: {result.unrecovered_failures}",
            f"- Violations: {', '.join(result.violations) or 'None'}",
            "",
            "| Cycle | Attempts | Rows | Recovered | Error |",
            "|---:|---:|---:|:---:|---|",
        ]
        lines.extend(
            f"| {cycle.cycle} | {cycle.attempts} | {cycle.completed_rows} | "
            f"{'Yes' if cycle.recovered else 'No'} | {cycle.error or '-'} |"
            for cycle in result.cycle_results
        )
        return "\n".join(lines) + "\n"


__all__ = ["RecoveryReportWriter"]
