"""Row- and time-based autosave policy."""

from __future__ import annotations

from collections.abc import Callable
from time import monotonic


class AutoSavePolicy:
    """Request persistence after enough writes or elapsed time."""

    def __init__(
        self,
        row_interval: int = 20,
        seconds_interval: float = 30.0,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if row_interval <= 0:
            raise ValueError("row_interval must be greater than zero")
        if seconds_interval <= 0:
            raise ValueError("seconds_interval must be greater than zero")
        self._row_interval = row_interval
        self._seconds_interval = seconds_interval
        self._clock = clock
        self._dirty_rows = 0
        self._last_save = clock()

    @property
    def dirty_rows(self) -> int:
        return self._dirty_rows

    def record_write(self) -> None:
        self._dirty_rows += 1

    def should_save(self) -> bool:
        if self._dirty_rows == 0:
            return False
        return (
            self._dirty_rows >= self._row_interval
            or self._clock() - self._last_save >= self._seconds_interval
        )

    def mark_saved(self) -> None:
        self._dirty_rows = 0
        self._last_save = self._clock()
