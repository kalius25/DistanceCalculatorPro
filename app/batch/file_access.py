"""Safe output-file validation and atomic replacement helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile

from app.logging import LoggingManager

logger = LoggingManager.get_logger(__name__)


@dataclass(frozen=True, slots=True)
class OutputWriteError(RuntimeError):
    """Raised when a result file cannot be safely persisted."""

    output_path: Path
    operation: str
    reason: str

    def __str__(self) -> str:
        return (
            f"Unable to {self.operation} result file '{self.output_path}'. "
            f"{self.reason} Close the file in Excel and retry, or choose Save As."
        )


class AtomicOutputFile:
    """Create a sibling temporary file and atomically replace the destination."""

    def __init__(self, output_path: Path) -> None:
        self.output_path = output_path
        self.temp_path: Path | None = None

    def create(self, *, suffix: str | None = None) -> Path:
        logger.debug(
            "ATOMIC_CREATE_BEGIN",
            extra={
                "event": "ATOMIC_CREATE_BEGIN",
                "output_path": str(self.output_path),
                "output_exists": self.output_path.exists(),
            },
        )
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="wb",
            prefix=f".{self.output_path.stem}.",
            suffix=suffix or self.output_path.suffix,
            dir=self.output_path.parent,
            delete=False,
        ) as stream:
            self.temp_path = Path(stream.name)
        logger.debug(
            "ATOMIC_CREATE_OK",
            extra={
                "event": "ATOMIC_CREATE_OK",
                "output_path": str(self.output_path),
                "temp_path": str(self.temp_path),
                "temp_exists": self.temp_path.is_file(),
            },
        )
        return self.temp_path

    def replace(self) -> None:
        if self.temp_path is None:
            logger.error(
                "ATOMIC_REPLACE_NO_TEMP",
                extra={
                    "event": "ATOMIC_REPLACE_NO_TEMP",
                    "output_path": str(self.output_path),
                },
            )
            raise RuntimeError("Temporary output file has not been created")
        if not self.temp_path.is_file():
            missing = self.temp_path
            logger.error(
                "ATOMIC_REPLACE_TEMP_MISSING",
                extra={
                    "event": "ATOMIC_REPLACE_TEMP_MISSING",
                    "output_path": str(self.output_path),
                    "temp_path": str(missing),
                },
            )
            self.temp_path = None
            raise OutputWriteError(
                self.output_path,
                "replace",
                f"Temporary result file was not created: '{missing}'.",
            )
        logger.debug(
            "ATOMIC_REPLACE_BEGIN",
            extra={
                "event": "ATOMIC_REPLACE_BEGIN",
                "output_path": str(self.output_path),
                "output_exists": self.output_path.exists(),
                "temp_path": str(self.temp_path),
                "temp_exists": self.temp_path.is_file(),
                "temp_size_bytes": self.temp_path.stat().st_size,
            },
        )
        try:
            # os.replace creates output_path when it does not exist and
            # atomically replaces it when it does.  A WinError 5 here means
            # the destination (or directory policy) denied replacement; it
            # does not mean the generated temporary workbook was missing.
            os.replace(self.temp_path, self.output_path)
        except (PermissionError, OSError) as error:
            logger.exception(
                "ATOMIC_REPLACE_FAILED",
                extra={
                    "event": "ATOMIC_REPLACE_FAILED",
                    "output_path": str(self.output_path),
                    "temp_path": str(self.temp_path),
                    "output_exists": self.output_path.exists(),
                    "error_type": type(error).__name__,
                    "error": str(error),
                },
            )
            self.cleanup()
            raise OutputWriteError(
                self.output_path,
                "replace",
                str(error),
            ) from error
        logger.debug(
            "ATOMIC_REPLACE_OK",
            extra={
                "event": "ATOMIC_REPLACE_OK",
                "output_path": str(self.output_path),
                "output_exists": self.output_path.is_file(),
                "output_size_bytes": self.output_path.stat().st_size,
            },
        )
        self.temp_path = None

    def cleanup(self) -> None:
        if self.temp_path is None:
            return
        try:
            self.temp_path.unlink(missing_ok=True)
        finally:
            self.temp_path = None


def ensure_output_writable(output_path: Path) -> None:
    """Verify the destination directory can create and remove a probe file."""
    logger.debug(
        "OUTPUT_WRITABLE_CHECK_BEGIN",
        extra={
            "event": "OUTPUT_WRITABLE_CHECK_BEGIN",
            "output_path": str(output_path),
            "output_exists": output_path.exists(),
        },
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with NamedTemporaryFile(
            mode="wb",
            prefix=".dcp-write-test-",
            dir=output_path.parent,
            delete=False,
        ) as stream:
            probe = Path(stream.name)
        probe.unlink()
        if output_path.exists():
            # Opening an existing destination for update is a harmless early
            # lock probe.  On Windows, Excel commonly denies this while the
            # workbook is open, allowing preflight to stop before a long batch
            # reaches its first autosave/atomic replace.
            with output_path.open("r+b"):
                pass
    except (PermissionError, OSError) as error:
        logger.exception(
            "OUTPUT_WRITABLE_CHECK_FAILED",
            extra={
                "event": "OUTPUT_WRITABLE_CHECK_FAILED",
                "output_path": str(output_path),
                "error_type": type(error).__name__,
                "error": str(error),
            },
        )
        raise OutputWriteError(output_path, "write", str(error)) from error
    logger.debug(
        "OUTPUT_WRITABLE_CHECK_OK",
        extra={
            "event": "OUTPUT_WRITABLE_CHECK_OK",
            "output_path": str(output_path),
            "output_exists": output_path.exists(),
        },
    )


__all__ = ["AtomicOutputFile", "OutputWriteError", "ensure_output_writable"]
