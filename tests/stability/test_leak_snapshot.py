import gc
from threading import Thread
from unittest.mock import patch

import pytest

from app.stability import LeakSnapshotCollector, WeakReferenceTracker
from app.stability.leak_snapshot import (
    _default_file_handles,
    _default_memory,
    _default_timestamp,
)

pytestmark = pytest.mark.stability


class Tracked:
    pass


def test_tracker_counts_and_prunes_dead_references() -> None:
    tracker = WeakReferenceTracker()
    value = Tracked()
    tracker.track(value)

    assert tracker.live_count == 1
    del value
    gc.collect()
    assert tracker.live_count == 0

    tracker.prune()
    assert tracker.live_count == 0


def test_collector_captures_injected_resources_and_clamps_memory() -> None:
    tracker = WeakReferenceTracker()
    value = Tracked()
    tracker.track(value)
    thread = Thread(name="worker")
    collector = LeakSnapshotCollector(
        tracker=tracker,
        timestamp_resolver=lambda: "now",
        memory_resolver=lambda: (-1, -2),
        thread_resolver=lambda: (thread,),
        gc_resolver=lambda: (4, 5, 6),
        file_handle_resolver=lambda: 7,
    )

    assert collector.tracker is tracker
    captured = collector.capture()
    assert captured.timestamp == "now"
    assert captured.current_memory_bytes == 0
    assert captured.peak_memory_bytes == 0
    assert captured.thread_count == 1
    assert captured.thread_names == ("worker",)
    assert captured.gc_counts == (4, 5, 6)
    assert captured.live_reference_count == 1
    assert captured.file_handle_count == 7


def test_default_memory_handles_inactive_and_active_tracing() -> None:
    with patch("app.stability.leak_snapshot.tracemalloc") as tracing:
        tracing.is_tracing.return_value = False
        assert _default_memory() == (0, 0)

        tracing.is_tracing.return_value = True
        tracing.get_traced_memory.return_value = (10, 20)
        assert _default_memory() == (10, 20)


def test_default_file_handles_handles_unsupported_and_os_error() -> None:
    with patch("app.stability.leak_snapshot.os.name", "nt"):
        assert _default_file_handles() is None

    with (
        patch("app.stability.leak_snapshot.os.name", "posix"),
        patch("app.stability.leak_snapshot.Path.is_dir", return_value=True),
        patch(
            "app.stability.leak_snapshot.Path.iterdir",
            side_effect=OSError("unavailable"),
        ),
    ):
        assert _default_file_handles() is None


def test_default_file_handles_counts_descriptors() -> None:
    with (
        patch("app.stability.leak_snapshot.os.name", "posix"),
        patch("app.stability.leak_snapshot.Path.is_dir", return_value=True),
        patch(
            "app.stability.leak_snapshot.Path.iterdir",
            return_value=iter((object(), object())),
        ),
    ):
        assert _default_file_handles() == 2


def test_default_timestamp_is_timezone_aware() -> None:
    assert _default_timestamp().endswith("+00:00")
