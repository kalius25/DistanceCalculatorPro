# Sprint 2.6.1-A/B — Workspace Layout Polish

## Changes

- When a workbook is loaded, `Show file panels` displays only Select Workbook,
  Recent Workbooks, and File Information; Workbook Inspector is hidden.
- Hiding the file panels restores Workbook Inspector and Data Preview.
- Batch Summary is positioned beside the File Workspace heading.
- The duplicate Retry Failed button was removed from Batch Summary; retry remains
  available from the main toolbar.
- Application version updated to `1.2.0-rc15`.

## Quality gate

Run on Windows:

```powershell
black .
ruff check .
mypy app
pytest
```
