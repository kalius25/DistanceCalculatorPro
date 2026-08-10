# Sprint 2.6.5 B — Result Duration + Open Result File

## Changes

- Column Mapping now exposes four roles:
  - Origin column
  - Destination column
  - Result distance
  - Result duration
- Route completion keeps both duration text and duration minutes from the selected best route.
- Excel and CSV result writers persist route duration into the mapped Result duration column.
- Live route activity shows travel time when a row completes.
- Final Completed/Stopped summary prompts with the exact saved result path and asks whether to open it.
- Choosing Yes opens the result through `QDesktopServices.openUrl(QUrl.fromLocalFile(...))`, so Windows uses the configured default application (Excel, WPS, etc.).
- Existing distinct-output policy remains unchanged: the input workbook is never reused as the output workbook.

## Validation

- `python -m compileall -q app tests`: PASS
- Batch/service targeted functional tests: PASS
- GUI tests are included/updated, but the sandbox cannot execute them because PySide6 is not installed in this environment.
