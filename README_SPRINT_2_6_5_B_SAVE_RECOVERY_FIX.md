# Sprint 2.6.5 B — Result Save / Save As Recovery Fix

## Reported issues

1. Autosave could fail on Windows when an existing `.result.xlsx` was open in Excel:
   `WinError 5 Access is denied` during atomic replacement.
2. Choosing **Save As...** after that failure could fail with:
   `cannot switch to a different thread (which happens to have exited)`.

## Root cause

`BatchCalculationService.calculate_queue()` flushed the result writer before calling
`calculation_service.finish_batch()` in the same `finally` block. If the final/autosave
flush raised `OutputWriteError`, execution skipped `finish_batch()`.

For the Google web provider this left sync Playwright resources bound to the worker
QThread that had just exited. A retry/Save As then ran in a new QThread and attempted
to reuse Playwright state owned by the dead thread, producing the cross-thread
greenlet error.

## Fix

- Nested the writer flush in its own `try/finally` so `finish_batch()` always runs,
  including when result persistence raises `OutputWriteError`.
- Extended `ensure_output_writable()` with a harmless update-open probe when the
  destination already exists. On Windows this catches the common Excel-lock case
  during preflight, before a long calculation reaches autosave.
- Added regression tests for flush failure cleanup and existing locked/writable
  destinations.

## Verification

- `python -m compileall -q app tests` — PASS
- Targeted tests:
  `pytest -q --no-cov tests/batch/test_file_access.py tests/services/test_batch_calculation_service.py`
  — **31 passed**
- Full GUI suite was not runnable in the sandbox because `PySide6` is not installed.
  Run the normal full suite on the project machine to confirm the retained 100%
  line/branch coverage baseline.
