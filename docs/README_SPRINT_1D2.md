# Sprint 1D.2 — Toolbar Execution Orchestration

## Goal

Make the main toolbar the only execution control surface while keeping HomePage as a passive workspace view.

## Architecture

- `MainWindow` owns `ExecutionState`.
- `HomePage` exposes `set_workspace_locked(bool)` and `workspace_locked`.
- `HomePage` contains no start, pause, resume, stop, controller, or calculation-service logic.
- Calculation actions emit immutable workspace configuration through presentation signals.

## State transitions

- `IDLE -> RUNNING`: Start, only when workspace configuration is ready.
- `RUNNING -> PAUSED`: Pause.
- `PAUSED -> RUNNING`: Resume.
- `RUNNING|PAUSED -> IDLE`: Stop.
- Invalid or duplicate transitions are ignored.

## Toolbar behavior

- Start: F5
- Pause/Resume: F6
- Stop: Shift+F5

While active, workbook selection, recent files, worksheet, preview rows, column mapping, and provider configuration are locked.

## Quality gate

```powershell
ruff check .
black --check .
mypy app
pytest
```
