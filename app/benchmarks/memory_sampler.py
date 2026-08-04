"""Portable peak-memory sampling based on :mod:`tracemalloc`."""

from __future__ import annotations

import tracemalloc


class MemorySampler:
    """Own one tracemalloc measurement session."""

    def __init__(self) -> None:
        self._started_here = False

    def start(self) -> None:
        if not tracemalloc.is_tracing():
            tracemalloc.start()
            self._started_here = True
        tracemalloc.reset_peak()

    def peak_bytes(self) -> int:
        if not tracemalloc.is_tracing():
            return 0
        return tracemalloc.get_traced_memory()[1]

    def stop(self) -> None:
        if self._started_here and tracemalloc.is_tracing():
            tracemalloc.stop()
        self._started_here = False


__all__ = ["MemorySampler"]
