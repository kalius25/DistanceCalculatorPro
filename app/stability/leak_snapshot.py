"""Resource snapshots and weak-reference tracking for stability tests."""

from __future__ import annotations

import gc
import os
import threading
import tracemalloc
import weakref
from collections.abc import Callable, Iterable
from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

from .models import LeakSnapshot


class WeakReferenceable(Protocol):
    """Object accepted by :class:`WeakReferenceTracker`."""

    __weakref__: object


TimestampResolver = Callable[[], str]
MemoryResolver = Callable[[], tuple[int, int]]
ThreadResolver = Callable[[], Iterable[threading.Thread]]
GcResolver = Callable[[], tuple[int, int, int]]
FileHandleResolver = Callable[[], int | None]


def _default_timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _default_memory() -> tuple[int, int]:
    if not tracemalloc.is_tracing():
        return 0, 0
    return tracemalloc.get_traced_memory()


def _default_file_handles() -> int | None:
    descriptor_directory = Path("/proc/self/fd")
    if os.name != "posix" or not descriptor_directory.is_dir():
        return None
    try:
        return sum(1 for _entry in descriptor_directory.iterdir())
    except OSError:
        return None


class WeakReferenceTracker:
    """Track objects without extending their lifetime."""

    def __init__(self) -> None:
        self._references: list[weakref.ReferenceType[object]] = []

    def track(self, value: WeakReferenceable) -> None:
        self._references.append(weakref.ref(value))

    @property
    def live_count(self) -> int:
        return sum(reference() is not None for reference in self._references)

    def prune(self) -> None:
        self._references = [
            reference for reference in self._references if reference() is not None
        ]


class LeakSnapshotCollector:
    """Capture deterministic resource snapshots with injectable resolvers."""

    def __init__(
        self,
        *,
        tracker: WeakReferenceTracker | None = None,
        timestamp_resolver: TimestampResolver = _default_timestamp,
        memory_resolver: MemoryResolver = _default_memory,
        thread_resolver: ThreadResolver = threading.enumerate,
        gc_resolver: GcResolver = gc.get_count,
        file_handle_resolver: FileHandleResolver = _default_file_handles,
    ) -> None:
        self._tracker = tracker or WeakReferenceTracker()
        self._timestamp_resolver = timestamp_resolver
        self._memory_resolver = memory_resolver
        self._thread_resolver = thread_resolver
        self._gc_resolver = gc_resolver
        self._file_handle_resolver = file_handle_resolver

    @property
    def tracker(self) -> WeakReferenceTracker:
        return self._tracker

    def capture(self) -> LeakSnapshot:
        current_memory, peak_memory = self._memory_resolver()
        threads = tuple(self._thread_resolver())
        return LeakSnapshot(
            timestamp=self._timestamp_resolver(),
            current_memory_bytes=max(current_memory, 0),
            peak_memory_bytes=max(peak_memory, 0),
            thread_count=len(threads),
            thread_names=tuple(thread.name for thread in threads),
            gc_counts=self._gc_resolver(),
            live_reference_count=self._tracker.live_count,
            file_handle_count=self._file_handle_resolver(),
        )


__all__ = ["LeakSnapshotCollector", "WeakReferenceTracker"]
