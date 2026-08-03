"""Safe output path generation for batch result workbooks."""

from __future__ import annotations

from pathlib import Path


class OutputPathPolicy:
    """Build a sibling result path without overwriting the source file."""

    def build(self, source_path: str | Path) -> Path:
        source = Path(source_path)
        stem = source.stem
        if stem.casefold().endswith(".result"):
            return source
        return source.with_name(f"{stem}.result{source.suffix}")
