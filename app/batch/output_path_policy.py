"""Safe output path generation for batch result workbooks."""

from __future__ import annotations

from pathlib import Path

from app.logging import LoggingManager

logger = LoggingManager.get_logger(__name__)


class OutputPathPolicy:
    """Build a sibling result path that is always distinct from the source."""

    def build(self, source_path: str | Path) -> Path:
        source = Path(source_path)
        output = source.with_name(f"{source.stem}.result{source.suffix}")
        logger.info(
            "OUTPUT_PATH_BUILT",
            extra={
                "event": "OUTPUT_PATH_BUILT",
                "source_path": str(source),
                "output_path": str(output),
                "paths_are_distinct": source != output,
            },
        )
        return output
