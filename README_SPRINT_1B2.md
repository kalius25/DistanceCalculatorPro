# Sprint 1B.2 — Workbook Inspector

The selected `.xlsx`, `.xlsm`, or `.csv` file is inspected through `WorkbookInspectorService`.
Presentation depends on immutable metadata models and does not import OpenPyXL.

## Quality gate

```powershell
ruff check app tests
black --check app tests
mypy app
pytest
```

## Run

```powershell
python -m app.presentation.app
```
