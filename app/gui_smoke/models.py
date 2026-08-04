"""Immutable results produced by GUI smoke scenarios."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True, slots=True)
class GuiSmokeResult:
    """Outcome of one deterministic GUI smoke scenario."""

    scenario: str
    passed: bool
    final_status: str
    final_state: str
    progress_events: int
    summary_events: int
    completed_events: int
    output_path: str
    error: str = ""

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


__all__ = ["GuiSmokeResult"]
