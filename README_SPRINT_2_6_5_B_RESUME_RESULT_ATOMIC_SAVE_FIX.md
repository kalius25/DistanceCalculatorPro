# Sprint 2.6.5 B — Resume Result / Atomic Save Fix

## Problem
When an existing `*.result.xlsx` was selected as the workbook to continue an unfinished calculation, Windows could reject the atomic promotion step:

`os.replace(<generated temp>, <existing result.xlsx>) -> WinError 5 Access is denied`

The random sibling name (for example `.result.4q83elyk.xlsx`) is a temporary workbook created by the current autosave. It is not expected to exist before the save starts.

## Fix
- ExcelResultWriter now loads the source workbook from an in-memory `BytesIO` snapshot rather than handing openpyxl the live source path for the lifetime of the writer.
- This prevents the writer from retaining a filesystem relationship/handle to the same `*.result.xlsx` that it later needs to atomically replace when resuming directly from a result file on Windows.
- AtomicOutputFile now explicitly verifies that the generated temporary file exists immediately before promotion.
- `os.replace()` remains the correct primitive: it creates the destination when absent and replaces it atomically when present.
- If the temp file is genuinely missing, the user now gets a specific temporary-file error instead of a misleading replace/lock diagnosis.

## Validation
- 22/22 targeted functional tests PASS (`--no-cov`).
- `python -m compileall` PASS.
- Added regression coverage for loading an existing `.result.xlsx` from an in-memory snapshot and for a genuinely missing generated temp file.

## Windows note
If another application such as Microsoft Excel actually has the destination workbook open, Windows can still legitimately deny replacement. In that case the file must be closed or another output path chosen.
