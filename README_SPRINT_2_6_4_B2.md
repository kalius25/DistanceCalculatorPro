# Sprint 2.6.4-B2 — Incremental Live Row Updates

## Scope

Connect the row-event contract introduced in B1 to the Data Preview status column.

## Behavior

- `CalculationExecutionCoordinator.row_event` is consumed by `MainWindow` when available.
- Each `RouteJobEvent.preview_row_index` is mapped directly to one zero-based Data Preview row.
- Job statuses map to preview states as follows:
  - `PENDING` -> `Pending`
  - `RUNNING` -> `Running`
  - `DONE` -> `Success`
  - `FAILED` -> `Failed`
  - `SKIPPED` -> `Skipped`
  - `RETRY` -> `Retried`
  - `INVALID` -> `Invalid`
- `HomePage.set_preview_row_status()` delegates to `ExcelTableModel.set_row_status()`, which emits `dataChanged` only for the status cell of the affected row.
- All preview statuses are reset before coordinator execution starts so early worker events cannot be overwritten by a later reset.
- Older/test coordinators without a `row_event` signal remain supported through optional signal discovery.

## Out of scope

- Auto-scroll
- Running-row highlight
- Status filtering
- Batch-summary synchronization changes

These remain for Sprint 2.6.4-C/D.
