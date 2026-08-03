"""JSON report persistence for headless end-to-end runs."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from .models import E2ERunReport


class E2EReportWriter:
    """Write deterministic, human-readable JSON reliability reports."""

    def __init__(self, output_directory: str | Path = "logs/e2e") -> None:
        self._output_directory = Path(output_directory)

    def write(self, report: E2ERunReport) -> Path:
        self._output_directory.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S_%f")
        path = self._output_directory / f"e2e-{report.scenario}-{timestamp}.json"
        path.write_text(
            json.dumps(report.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path


__all__ = ["E2EReportWriter"]
