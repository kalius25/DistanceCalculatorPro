from pathlib import Path
from unittest.mock import patch

import pytest

from app.batch.file_access import (
    AtomicOutputFile,
    OutputWriteError,
    ensure_output_writable,
)


def test_output_write_error_message(tmp_path: Path) -> None:
    error = OutputWriteError(tmp_path / "routes.xlsx", "save", "locked")
    assert "Unable to save result file" in str(error)
    assert "Close the file in Excel" in str(error)


def test_atomic_output_file_creates_replaces_and_cleans(tmp_path: Path) -> None:
    output = tmp_path / "routes.result.csv"
    atomic = AtomicOutputFile(output)
    temporary = atomic.create()
    temporary.write_text("new", encoding="utf-8")
    atomic.replace()
    assert output.read_text(encoding="utf-8") == "new"
    assert atomic.temp_path is None

    temporary = atomic.create(suffix=".tmp")
    assert temporary.suffix == ".tmp"
    atomic.cleanup()
    assert not temporary.exists()
    atomic.cleanup()


def test_atomic_output_file_requires_temp_and_wraps_replace_failure(
    tmp_path: Path,
) -> None:
    atomic = AtomicOutputFile(tmp_path / "routes.result.xlsx")
    with pytest.raises(RuntimeError, match="has not been created"):
        atomic.replace()

    temporary = atomic.create()
    temporary.write_text("new", encoding="utf-8")
    with patch(
        "app.batch.file_access.os.replace", side_effect=PermissionError("locked")
    ):
        with pytest.raises(OutputWriteError, match="Unable to replace"):
            atomic.replace()
    assert atomic.temp_path is None
    assert not temporary.exists()


def test_ensure_output_writable_accepts_directory_and_wraps_failure(
    tmp_path: Path,
) -> None:
    output = tmp_path / "nested" / "routes.xlsx"
    ensure_output_writable(output)
    assert output.parent.exists()

    with patch(
        "app.batch.file_access.NamedTemporaryFile",
        side_effect=PermissionError("denied"),
    ):
        with pytest.raises(OutputWriteError, match="Unable to write"):
            ensure_output_writable(output)
