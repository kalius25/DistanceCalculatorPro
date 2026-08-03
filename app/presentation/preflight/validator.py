"""Batch resource preflight validation."""

from __future__ import annotations

import shutil
from collections.abc import Callable
from pathlib import Path

from app.batch import OutputWriteError, ensure_output_writable

from .models import PreflightIssue, PreflightPolicy, PreflightResult

DiskFreeResolver = Callable[[Path], int]
WritableValidator = Callable[[Path], None]


def _default_disk_free(path: Path) -> int:
    existing = path
    while not existing.exists() and existing != existing.parent:
        existing = existing.parent
    return shutil.disk_usage(existing).free


class BatchPreflightValidator:
    """Estimate resource requirements and reject unsafe batch starts."""

    def __init__(
        self,
        policy: PreflightPolicy | None = None,
        *,
        disk_free_resolver: DiskFreeResolver | None = None,
        writable_validator: WritableValidator = ensure_output_writable,
    ) -> None:
        self._policy = policy or PreflightPolicy()
        self._disk_free_resolver = disk_free_resolver or _default_disk_free
        self._writable_validator = writable_validator

    @property
    def policy(self) -> PreflightPolicy:
        return self._policy

    def validate(
        self,
        *,
        source_path: str | Path,
        output_path: str | Path,
        estimated_job_count: int,
        source_size_bytes: int | None = None,
    ) -> PreflightResult:
        source = Path(source_path)
        output = Path(output_path)
        job_count = max(int(estimated_job_count), 0)
        source_size = (
            max(int(source_size_bytes), 0)
            if source_size_bytes is not None
            else (source.stat().st_size if source.exists() else 0)
        )
        estimated_output = max(
            source_size,
            job_count * self._policy.estimated_bytes_per_job,
        )
        required = (
            int(estimated_output * self._policy.output_size_multiplier)
            + self._policy.minimum_reserved_bytes
        )
        issues: list[PreflightIssue] = []

        try:
            self._writable_validator(output)
        except OutputWriteError as error:
            issues.append(
                PreflightIssue(
                    code="output_not_writable",
                    title="Output location is not writable",
                    message=str(error),
                    blocking=True,
                )
            )

        available: int | None
        try:
            available = max(self._disk_free_resolver(output.parent), 0)
        except OSError as error:
            available = None
            issues.append(
                PreflightIssue(
                    code="disk_space_unknown",
                    title="Disk space could not be verified",
                    message=(
                        f"DistanceCalculatorPro could not read free space for "
                        f"'{output.parent}'. {error}"
                    ),
                    blocking=False,
                )
            )
        else:
            if available < required:
                issues.append(
                    PreflightIssue(
                        code="insufficient_disk_space",
                        title="Insufficient disk space",
                        message=(
                            "The calculation cannot start because the output "
                            "location does not have enough free space."
                        ),
                        blocking=True,
                    )
                )

        if job_count >= self._policy.large_batch_job_count:
            issues.append(
                PreflightIssue(
                    code="large_batch",
                    title="Large batch detected",
                    message=(
                        f"This workbook contains approximately {job_count:,} jobs. "
                        "The calculation may run for a long time and generate "
                        "significant disk activity."
                    ),
                    blocking=False,
                )
            )

        return PreflightResult(
            output_path=output,
            estimated_job_count=job_count,
            estimated_output_bytes=estimated_output,
            required_free_bytes=required,
            available_bytes=available,
            issues=tuple(issues),
        )


__all__ = ["BatchPreflightValidator"]
