"""JSON and Markdown reports for benchmark regression comparisons."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .regression_models import RegressionComparison


class RegressionReportWriter:
    """Persist performance comparison reports."""

    def write(
        self,
        comparisons: list[RegressionComparison],
        directory: str | Path,
        *,
        stem: str | None = None,
    ) -> tuple[Path, Path]:
        target = Path(directory)
        target.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now(UTC)
        resolved_stem = stem or created_at.strftime(
            "regression-report-%Y%m%d-%H%M%S-%f"
        )
        json_path = target / f"{resolved_stem}.json"
        markdown_path = target / f"{resolved_stem}.md"
        payload = {
            "created_at": created_at.isoformat(),
            "comparisons": [comparison.to_dict() for comparison in comparisons],
        }
        json_path.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        markdown_path.write_text(
            self._render_markdown(comparisons),
            encoding="utf-8",
        )
        return json_path, markdown_path

    @staticmethod
    def _render_markdown(comparisons: list[RegressionComparison]) -> str:
        lines = [
            "# Performance Regression Report",
            "",
            "| Scenario | Status | Runtime | Memory | Throughput | Autosaves |",
            "|---|:---:|---:|---:|---:|---:|",
        ]
        for comparison in comparisons:
            lines.append(
                f"| {comparison.scenario} | {comparison.status.value} | "
                f"{comparison.runtime_change_percent:+.2f}% | "
                f"{comparison.memory_change_percent:+.2f}% | "
                f"{comparison.throughput_change_percent:+.2f}% | "
                f"{comparison.autosave_delta:+d} |"
            )
        return "\n".join(lines) + "\n"


__all__ = ["RegressionReportWriter"]
