"""Safe output path generation for batch result workbooks."""

from __future__ import annotations

from pathlib import Path


class OutputPathPolicy:
    """Build a sibling result path without overwriting the source file."""

    def build(self, source_path: str | Path) -> Path:
        source = Path(source_path)
        return source.with_name(f"{source.stem}.result{source.suffix}")
