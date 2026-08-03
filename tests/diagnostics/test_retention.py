from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.diagnostics import (
    DiagnosticsRetentionManager,
    DiagnosticsRetentionPolicy,
)


def write_artifact(path: Path, content: bytes, timestamp: int) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    os.utime(path, ns=(timestamp, timestamp))


def test_retention_policy_rejects_invalid_limits() -> None:
    with pytest.raises(ValueError, match="files must be positive"):
        DiagnosticsRetentionPolicy(max_files=0)
    with pytest.raises(ValueError, match="bytes must be positive"):
        DiagnosticsRetentionPolicy(max_total_bytes=0)


def test_retention_manager_deletes_oldest_files_by_count(tmp_path: Path) -> None:
    manager = DiagnosticsRetentionManager(
        tmp_path,
        DiagnosticsRetentionPolicy(max_files=2, max_total_bytes=100),
    )
    first = tmp_path / "html" / "first.html"
    second = tmp_path / "json" / "second.json"
    third = tmp_path / "screenshots" / "third.png"
    write_artifact(first, b"111", 1)
    manager.register(first)
    write_artifact(second, b"22", 2)
    manager.register(second)
    write_artifact(third, b"3", 3)

    snapshot = manager.register(third)

    assert not first.exists()
    assert second.exists()
    assert third.exists()
    assert snapshot.files_created == 3
    assert snapshot.bytes_created == 6
    assert snapshot.files_deleted == 1
    assert snapshot.bytes_deleted == 3
    assert snapshot.current_files == 2
    assert snapshot.current_bytes == 3


def test_retention_manager_deletes_by_size_and_enforces_existing_files(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first.json"
    second = tmp_path / "second.json"
    write_artifact(first, b"1234", 1)
    write_artifact(second, b"5678", 2)
    manager = DiagnosticsRetentionManager(
        tmp_path,
        DiagnosticsRetentionPolicy(max_files=10, max_total_bytes=5),
    )

    snapshot = manager.enforce()

    assert not first.exists()
    assert second.exists()
    assert snapshot.files_created == 0
    assert snapshot.files_deleted == 1
    assert snapshot.current_bytes == 4


def test_retention_snapshot_is_empty_when_directory_is_missing(
    tmp_path: Path,
) -> None:
    manager = DiagnosticsRetentionManager(tmp_path / "missing")

    assert manager.snapshot.current_files == 0
    assert manager.snapshot.current_bytes == 0
