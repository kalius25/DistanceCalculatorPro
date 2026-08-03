"""JSON persistence for synthetic benchmark results."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .models import BatchBenchmarkResult


class BenchmarkReportWriter:
    """Persist one or more benchmark results as JSON."""

    def __init__(self, output_directory: str | Path = "logs/benchmarks") -> None:
        self._output_directory = Path(output_directory)

    def write(self, results: list[BatchBenchmarkResult]) -> Path:
        self._output_directory.mkdir(parents=True, exist_ok=True)
        created_at = datetime.now(UTC)
        path = self._output_directory / (
            f"batch-benchmark-{created_at.strftime('%Y%m%d_%H%M%S_%f')}.json"
        )
        payload = {
            "created_at": created_at.isoformat(),
            "results": [result.to_dict() for result in results],
        }
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


__all__ = ["BenchmarkReportWriter"]
