"""Immutable models for benchmark baseline creation and updates."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from pathlib import Path


class BaselineUpdateMode(StrEnum):
    """Supported baseline update strategies."""

    CREATE = "create"
    MERGE = "merge"
    REPLACE = "replace"


@dataclass(frozen=True, slots=True)
class BaselineUpdateResult:
    """Outcome of one baseline creation or update operation."""

    mode: BaselineUpdateMode
    output_path: Path
    dry_run: bool
    added: tuple[str, ...] = ()
    updated: tuple[str, ...] = ()
    retained: tuple[str, ...] = ()
    removed: tuple[str, ...] = ()
    requested_scenarios: tuple[str, ...] = ()
    selected_scenarios: tuple[str, ...] = ()
    missing_scenarios: tuple[str, ...] = ()
    ignored_missing_scenarios: bool = False

    @property
    def changed(self) -> bool:
        return bool(self.added or self.updated or self.removed)

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["mode"] = self.mode.value
        payload["output_path"] = str(self.output_path)
        return payload


__all__ = ["BaselineUpdateMode", "BaselineUpdateResult"]
