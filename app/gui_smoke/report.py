"""JSON reporting for GUI smoke scenarios."""

from __future__ import annotations

import json
from pathlib import Path

from .models import GuiSmokeResult


class GuiSmokeReportWriter:
    """Persist one GUI smoke result as human-readable JSON."""

    def write(self, result: GuiSmokeResult, path: str | Path) -> Path:
        output = Path(path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(result.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return output


__all__ = ["GuiSmokeReportWriter"]
