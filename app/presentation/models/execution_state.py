from __future__ import annotations

from enum import Enum, auto


class ExecutionState(Enum):
    """Execution state of the calculation workflow."""

    IDLE = auto()
    RUNNING = auto()
    PAUSED = auto()