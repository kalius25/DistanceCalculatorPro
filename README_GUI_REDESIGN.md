# Sprint 1B.2 — Workspace GUI Redesign

## Delivered

- Removed the redundant **Change** button.
- Reorganized the workspace into three compact top panels:
  - Select Workbook
  - Recent Workbooks
  - File Information
- Added a full-width Workbook Inspector below the selection area.
- Added a bounded data preview using `QTableView` and `QStandardItemModel`.
- Excel and CSV readers retain at most the first 10 data rows per sheet.
- Added sheet-level summary information and header detection status.
- Added a Clear Recent List action in the workspace.
- Updated Light and Dark themes for the new components.
- Updated version to `1.2.0-alpha5`.

## Run

```powershell
python -m app.presentation.app
```

## Quality gate

```powershell
ruff check app tests
black --check app tests
mypy app
pytest
```
