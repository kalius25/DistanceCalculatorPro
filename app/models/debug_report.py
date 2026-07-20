"""
Debug report model.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class DebugReport:
    """
    Contains diagnostic information collected when an error occurs.
    """

    url: str | None = None

    html_file: Path | None = None

    screenshot_file: Path | None = None

    parser_report_file: Path | None = None

    error_message: str | None = None
