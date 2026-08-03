"""Runtime metrics for incremental result persistence."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AutosaveSnapshot:
    saves_completed: int
    rows_saved: int
    last_rows_saved: int
    total_save_seconds: float
    average_save_seconds: float
    maximum_save_seconds: float


@dataclass(slots=True)
class AutosaveMetrics:
    saves_completed: int = 0
    rows_saved: int = 0
    last_rows_saved: int = 0
    total_save_seconds: float = 0.0
    maximum_save_seconds: float = 0.0

    @property
    def snapshot(self) -> AutosaveSnapshot:
        average = (
            self.total_save_seconds / self.saves_completed
            if self.saves_completed
            else 0.0
        )
        return AutosaveSnapshot(
            saves_completed=self.saves_completed,
            rows_saved=self.rows_saved,
            last_rows_saved=self.last_rows_saved,
            total_save_seconds=self.total_save_seconds,
            average_save_seconds=average,
            maximum_save_seconds=self.maximum_save_seconds,
        )

    def record(self, rows_saved: int, elapsed_seconds: float) -> None:
        elapsed = max(elapsed_seconds, 0.0)
        rows = max(rows_saved, 0)
        self.saves_completed += 1
        self.rows_saved += rows
        self.last_rows_saved = rows
        self.total_save_seconds += elapsed
        self.maximum_save_seconds = max(self.maximum_save_seconds, elapsed)


__all__ = ["AutosaveMetrics", "AutosaveSnapshot"]
