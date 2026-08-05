"""Machine- and human-readable reports for the CI performance gate."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .gate_models import PerformanceGateResult


class PerformanceGateReportWriter:
    """Write a stable JSON and Markdown report pair."""

    def write(
        self,
        result: PerformanceGateResult,
        directory: str | Path,
        *,
        stem: str = "performance-gate",
    ) -> tuple[Path, Path]:
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now(UTC).isoformat()
        json_path = target / f"{stem}.json"
        markdown_path = target / f"{stem}.md"
        payload = {"created_at": created_at, **result.to_dict()}
        json_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        markdown_path.write_text(
            self._render_markdown(result),
            encoding="utf-8",
        )
        return json_path, markdown_path

    @staticmethod
    def _render_markdown(result: PerformanceGateResult) -> str:
        lines = [
            "# Performance Gate Report",
            "",
            f"**Status:** {result.status.value}",
            f"**Exit code:** {int(result.exit_code)}",
            f"**Fail on warning:** {str(result.fail_on_warning).lower()}",
            "",
            "| Scenario | Status | Runtime | Memory | Throughput | Autosaves |",
            "|---|:---:|---:|---:|---:|---:|",
        ]
        for item in result.comparisons:
            lines.append(
                f"| {item.scenario} | {item.status.value} | "
                f"{item.runtime_change_percent:+.2f}% | "
                f"{item.memory_change_percent:+.2f}% | "
                f"{item.throughput_change_percent:+.2f}% | "
                f"{item.autosave_delta:+d} |"
            )
        return "\n".join(lines) + "\n"


__all__ = ["PerformanceGateReportWriter"]
