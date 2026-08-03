"""Retention policy and metrics for diagnostic artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class DiagnosticsRetentionPolicy:
    """Limits applied to all files below one diagnostics directory."""

    max_files: int = 500
    max_total_bytes: int = 512 * 1024 * 1024

    def __post_init__(self) -> None:
        if self.max_files < 1:
            raise ValueError("Maximum diagnostic files must be positive.")
        if self.max_total_bytes < 1:
            raise ValueError("Maximum diagnostic bytes must be positive.")


@dataclass(frozen=True, slots=True)
class DiagnosticsRetentionSnapshot:
    """Current and lifetime diagnostics retention counters."""

    files_created: int
    bytes_created: int
    files_deleted: int
    bytes_deleted: int
    current_files: int
    current_bytes: int


class DiagnosticsRetentionManager:
    """Delete the oldest diagnostic files when configured limits are exceeded."""

    def __init__(
        self,
        root_directory: str | Path,
        policy: DiagnosticsRetentionPolicy | None = None,
    ) -> None:
        self._root_directory = Path(root_directory)
        self._policy = policy or DiagnosticsRetentionPolicy()
        self._files_created = 0
        self._bytes_created = 0
        self._files_deleted = 0
        self._bytes_deleted = 0

    @property
    def snapshot(self) -> DiagnosticsRetentionSnapshot:
        files = self._artifact_files()
        return DiagnosticsRetentionSnapshot(
            files_created=self._files_created,
            bytes_created=self._bytes_created,
            files_deleted=self._files_deleted,
            bytes_deleted=self._bytes_deleted,
            current_files=len(files),
            current_bytes=sum(path.stat().st_size for path in files),
        )

    def register(self, path: str | Path) -> DiagnosticsRetentionSnapshot:
        artifact = Path(path)
        size = artifact.stat().st_size
        self._files_created += 1
        self._bytes_created += size
        self._enforce()
        return self.snapshot

    def enforce(self) -> DiagnosticsRetentionSnapshot:
        self._enforce()
        return self.snapshot

    def _enforce(self) -> None:
        files = self._artifact_files()
        total_bytes = sum(path.stat().st_size for path in files)
        while (
            len(files) > self._policy.max_files
            or total_bytes > self._policy.max_total_bytes
        ):
            oldest = files.pop(0)
            size = oldest.stat().st_size
            oldest.unlink()
            self._files_deleted += 1
            self._bytes_deleted += size
            total_bytes -= size

    def _artifact_files(self) -> list[Path]:
        if not self._root_directory.exists():
            return []
        return sorted(
            (path for path in self._root_directory.rglob("*") if path.is_file()),
            key=lambda path: (path.stat().st_mtime_ns, str(path)),
        )


__all__ = [
    "DiagnosticsRetentionManager",
    "DiagnosticsRetentionPolicy",
    "DiagnosticsRetentionSnapshot",
]
