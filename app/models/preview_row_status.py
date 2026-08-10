"""Processing status values displayed by the Data Preview grid."""

from __future__ import annotations

from enum import Enum


class PreviewRowStatus(Enum):
    """Visual lifecycle state for one Data Preview row."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    INVALID = "invalid"
    RETRIED = "retried"

    @property
    def label(self) -> str:
        return {
            PreviewRowStatus.PENDING: "Pending",
            PreviewRowStatus.RUNNING: "Running",
            PreviewRowStatus.SUCCESS: "Success",
            PreviewRowStatus.FAILED: "Failed",
            PreviewRowStatus.SKIPPED: "Skipped",
            PreviewRowStatus.INVALID: "Invalid",
            PreviewRowStatus.RETRIED: "Retried",
        }[self]

    @property
    def symbol(self) -> str:
        return {
            PreviewRowStatus.PENDING: "○",
            PreviewRowStatus.RUNNING: "●",
            PreviewRowStatus.SUCCESS: "✓",
            PreviewRowStatus.FAILED: "✕",
            PreviewRowStatus.SKIPPED: "—",
            PreviewRowStatus.INVALID: "!",
            PreviewRowStatus.RETRIED: "↻",
        }[self]


__all__ = ["PreviewRowStatus"]
