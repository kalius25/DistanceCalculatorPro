"""Incremental workbook result writers."""

from __future__ import annotations

import csv
from abc import ABC, abstractmethod
from pathlib import Path
from time import perf_counter

from openpyxl import load_workbook
from openpyxl.workbook.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet

from .autosave_metrics import AutosaveMetrics, AutosaveSnapshot
from .autosave_policy import AutoSavePolicy
from .file_access import AtomicOutputFile, OutputWriteError, ensure_output_writable
from .models import RouteJob, RouteJobStatus
from .output_path_policy import OutputPathPolicy


class BaseResultWriter(ABC):
    """Write route-job outcomes and persist them incrementally."""

    def __init__(
        self,
        output_path: Path,
        autosave_policy: AutoSavePolicy | None = None,
    ) -> None:
        self.output_path = output_path
        self._autosave_policy = autosave_policy or AutoSavePolicy()
        self._dirty = False
        self._closed = False
        self._autosave_metrics = AutosaveMetrics()

    @property
    def dirty(self) -> bool:
        return self._dirty

    @property
    def closed(self) -> bool:
        return self._closed

    @property
    def autosave_metrics(self) -> AutosaveSnapshot:
        return self._autosave_metrics.snapshot

    def write(self, job: RouteJob) -> bool:
        value = self._value_for(job)
        if value is None:
            return False
        self._write_value(job, value)
        self._dirty = True
        self._autosave_policy.record_write()
        if self._autosave_policy.should_save():
            self.flush()
        return True

    def flush(self) -> bool:
        if self._closed or not self._dirty:
            return False
        ensure_output_writable(self.output_path)
        dirty_rows = self._autosave_policy.dirty_rows
        started_at = perf_counter()
        self._save()
        elapsed = perf_counter() - started_at
        self._autosave_metrics.record(dirty_rows, elapsed)
        self._dirty = False
        self._autosave_policy.mark_saved()
        return True

    def close(self) -> None:
        if self._closed:
            return
        self.flush()
        self._close()
        self._closed = True

    def __enter__(self) -> BaseResultWriter:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()

    @staticmethod
    def _value_for(job: RouteJob) -> float | str | None:
        if job.status is RouteJobStatus.DONE:
            return job.result_distance_km
        if job.status in {RouteJobStatus.FAILED, RouteJobStatus.INVALID}:
            return f"ERROR: {job.validation_error or 'Unknown error.'}"
        return None

    @abstractmethod
    def _write_value(self, job: RouteJob, value: float | str) -> None:
        """Write one value into the in-memory document."""

    @abstractmethod
    def _save(self) -> None:
        """Persist the in-memory document to output_path."""

    def _close(self) -> None:
        """Release resources after the final flush."""


class ExcelResultWriter(BaseResultWriter):
    """Keep one openpyxl workbook alive for a complete batch."""

    def __init__(
        self,
        source_path: str | Path,
        sheet_name: str,
        output_path: Path,
        autosave_policy: AutoSavePolicy | None = None,
    ) -> None:
        source = Path(source_path)
        self._workbook: Workbook = load_workbook(
            source,
            data_only=False,
            keep_vba=source.suffix.casefold() == ".xlsm",
        )
        if sheet_name not in self._workbook.sheetnames:
            self._workbook.close()
            raise ValueError(f"Worksheet not found: {sheet_name}")
        self._worksheet: Worksheet = self._workbook[sheet_name]
        self._columns = self._header_columns(self._worksheet)
        super().__init__(output_path, autosave_policy)

    def _write_value(self, job: RouteJob, value: float | str) -> None:
        column = self._columns.get(job.result_column)
        if column is None:
            raise ValueError(f"Result column not found: {job.result_column}")
        self._worksheet.cell(row=job.row_index, column=column, value=value)

    def _save(self) -> None:
        atomic = AtomicOutputFile(self.output_path)
        temporary = atomic.create(suffix=self.output_path.suffix)
        try:
            self._workbook.save(temporary)
            atomic.replace()
        except OutputWriteError:
            raise
        except (PermissionError, OSError) as error:
            atomic.cleanup()
            raise OutputWriteError(
                self.output_path,
                "save",
                str(error),
            ) from error
        except Exception:
            atomic.cleanup()
            raise

    def _close(self) -> None:
        self._workbook.close()

    @staticmethod
    def _header_columns(worksheet: Worksheet) -> dict[str, int]:
        return {
            str(cell.value).strip(): cell.column
            for cell in worksheet[1]
            if cell.value is not None
        }


class CsvResultWriter(BaseResultWriter):
    """Maintain CSV rows in memory and rewrite the output on autosave."""

    def __init__(
        self,
        source_path: str | Path,
        output_path: Path,
        autosave_policy: AutoSavePolicy | None = None,
    ) -> None:
        source = Path(source_path)
        with source.open("r", encoding="utf-8-sig", newline="") as stream:
            self._rows = list(csv.reader(stream))
        if not self._rows:
            raise ValueError("CSV file does not contain a header row")
        self._columns = {
            header.strip(): index for index, header in enumerate(self._rows[0])
        }
        super().__init__(output_path, autosave_policy)

    def _write_value(self, job: RouteJob, value: float | str) -> None:
        column = self._columns.get(job.result_column)
        if column is None:
            raise ValueError(f"Result column not found: {job.result_column}")
        row_index = job.row_index - 1
        if row_index < 1 or row_index >= len(self._rows):
            raise ValueError(f"CSV row not found: {job.row_index}")
        row = self._rows[row_index]
        while len(row) <= column:
            row.append("")
        row[column] = str(value)

    def _save(self) -> None:
        atomic = AtomicOutputFile(self.output_path)
        temporary = atomic.create(suffix=self.output_path.suffix)
        try:
            with temporary.open(
                "w",
                encoding="utf-8-sig",
                newline="",
            ) as stream:
                csv.writer(stream).writerows(self._rows)
            atomic.replace()
        except OutputWriteError:
            raise
        except (PermissionError, OSError) as error:
            atomic.cleanup()
            raise OutputWriteError(
                self.output_path,
                "save",
                str(error),
            ) from error
        except Exception:
            atomic.cleanup()
            raise


class ResultWriterFactory:
    """Create the correct writer for a supported workbook type."""

    def __init__(
        self,
        output_path_policy: OutputPathPolicy | None = None,
    ) -> None:
        self._output_path_policy = output_path_policy or OutputPathPolicy()

    def create(
        self,
        source_path: str | Path,
        sheet_name: str,
        autosave_policy: AutoSavePolicy | None = None,
        *,
        resume_from_output: bool = False,
        output_path: str | Path | None = None,
    ) -> BaseResultWriter:
        source = Path(source_path)
        output = (
            Path(output_path)
            if output_path is not None
            else self._output_path_policy.build(source)
        )
        input_path = output if resume_from_output and output.exists() else source
        suffix = source.suffix.casefold()
        if suffix in {".xlsx", ".xlsm"}:
            return ExcelResultWriter(
                input_path,
                sheet_name,
                output,
                autosave_policy,
            )
        if suffix == ".csv":
            return CsvResultWriter(input_path, output, autosave_policy)
        raise ValueError(f"Unsupported workbook type: {source.suffix}")


__all__ = [
    "BaseResultWriter",
    "CsvResultWriter",
    "ExcelResultWriter",
    "ResultWriterFactory",
]
