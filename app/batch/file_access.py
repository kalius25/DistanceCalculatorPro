"""Safe output-file validation and atomic replacement helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from tempfile import NamedTemporaryFile


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
        self.output_path.parent.mkdir(parents=True, exist_ok=True)
        with NamedTemporaryFile(
            mode="wb",
            prefix=f".{self.output_path.stem}.",
            suffix=suffix or self.output_path.suffix,
            dir=self.output_path.parent,
            delete=False,
        ) as stream:
            self.temp_path = Path(stream.name)
        return self.temp_path

    def replace(self) -> None:
        if self.temp_path is None:
            raise RuntimeError("Temporary output file has not been created")
        try:
            os.replace(self.temp_path, self.output_path)
        except (PermissionError, OSError) as error:
            self.cleanup()
            raise OutputWriteError(
                self.output_path,
                "replace",
                str(error),
            ) from error
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
    except (PermissionError, OSError) as error:
        raise OutputWriteError(output_path, "write", str(error)) from error


__all__ = ["AtomicOutputFile", "OutputWriteError", "ensure_output_writable"]
