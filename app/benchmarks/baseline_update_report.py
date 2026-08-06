"""JSON and Markdown reports for baseline update operations."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .baseline_update_models import BaselineUpdateResult


class BaselineUpdateReportWriter:
    """Persist baseline update summaries."""

    def write(
        self,
        result: BaselineUpdateResult,
        output_directory: str | Path,
    ) -> tuple[Path, Path]:
        directory = Path(output_directory)
        directory.mkdir(parents=True, exist_ok=True)
        json_path = directory / "baseline-update.json"
        markdown_path = directory / "baseline-update.md"
        payload = {
            "created_at": datetime.now(UTC).isoformat(),
            **result.to_dict(),
        }
        json_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        markdown_path.write_text(self._render_markdown(result), encoding="utf-8")
        return json_path, markdown_path

    @staticmethod
    def _render_markdown(result: BaselineUpdateResult) -> str:
        def names(values: tuple[str, ...]) -> str:
            return ", ".join(values) if values else "None"

        return "\n".join(
            (
                "# Benchmark Baseline Update",
                "",
                f"- Mode: {result.mode.value}",
                f"- Dry run: {result.dry_run}",
                f"- Output: {result.output_path}",
                f"- Added: {names(result.added)}",
                f"- Updated: {names(result.updated)}",
                f"- Retained: {names(result.retained)}",
                f"- Removed: {names(result.removed)}",
                f"- Requested scenarios: {names(result.requested_scenarios)}",
                f"- Selected scenarios: {names(result.selected_scenarios)}",
                f"- Missing scenarios: {names(result.missing_scenarios)}",
                ("- Ignored missing scenarios: " f"{result.ignored_missing_scenarios}"),
                "",
            )
        )


__all__ = ["BaselineUpdateReportWriter"]
