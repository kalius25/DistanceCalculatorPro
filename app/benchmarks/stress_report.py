"""JSON and Markdown reports for stress benchmark results."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .stress_models import StressBenchmarkResult


class StressBenchmarkReportWriter:
    """Persist benchmark results in machine- and human-readable formats."""

    def __init__(self, output_directory: str | Path = "logs/benchmarks") -> None:
        self._output_directory = Path(output_directory)

    def write(
        self,
        results: list[StressBenchmarkResult],
        *,
        stem: str | None = None,
    ) -> tuple[Path, Path]:
        self._output_directory.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now(UTC)
        report_stem = stem or (
            f"stress-benchmark-{created_at.strftime('%Y%m%d_%H%M%S_%f')}"
        )
        json_path = self._output_directory / f"{report_stem}.json"
        markdown_path = self._output_directory / f"{report_stem}.md"
        payload = {
            "created_at": created_at.isoformat(),
            "results": [result.to_dict() for result in results],
        }
        json_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        markdown_path.write_text(
            self._render_markdown(results),
            encoding="utf-8",
        )
        return json_path, markdown_path

    @staticmethod
    def _render_markdown(results: list[StressBenchmarkResult]) -> str:
        lines = [
            "# DistanceCalculatorPro Stress Benchmark",
            "",
            "| Scenario | Rows | Iterations | Seconds | Rows/s | Peak MB | Autosaves |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
        for result in results:
            lines.append(
                "| "
                f"{result.scenario} | {result.rows:,} | {result.iterations:,} | "
                f"{result.elapsed_seconds:.3f} | {result.rows_per_second:.2f} | "
                f"{result.peak_memory_mb:.2f} | {result.autosave_count:,} |"
            )
        return "\n".join(lines) + "\n"


__all__ = ["StressBenchmarkReportWriter"]
