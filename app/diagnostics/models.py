from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .retention import DiagnosticsRetentionPolicy


@dataclass(frozen=True, slots=True)
class DiagnosticsSettings:
    enabled: bool = False
    trace_browser: bool = False
    parser_diagnostics: bool = False
    save_html: bool = False
    save_screenshot: bool = False
    save_json: bool = False
    output_directory: Path = Path("logs/debug")
    retention_policy: DiagnosticsRetentionPolicy = DiagnosticsRetentionPolicy()
