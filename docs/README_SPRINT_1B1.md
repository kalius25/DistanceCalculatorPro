# Sprint 1B.1 — Workspace UI

## Objective

Replace the Home placeholder with the first usable file workspace while keeping
workbook parsing outside the Presentation layer.

## Delivered

- Drag-and-drop area for one local workbook.
- Native file browser for `.xlsx`, `.xlsm`, and `.csv` files.
- Selected-workbook summary card.
- Recent-workbook list in the Home workspace.
- Existing File > Recent Files menu connected to real file selection.
- Missing-file and unsupported-format validation.
- Light and Dark theme styling for all new components.
- Presentation unit tests for workspace state, signals, file validation,
  drag-and-drop, browsing, and MainWindow integration.

## Architectural boundary

Sprint 1B.1 selects and validates a file path only. It does not open, parse, or
preview workbook content. Workbook inspection belongs to Sprint 1B.2 and data
preview belongs to Sprint 1B.3.

## Quality gate

```powershell
ruff check app tests
black --check app tests
mypy app
pytest
```
