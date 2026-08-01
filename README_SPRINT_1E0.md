# Sprint 1E.0 — Calculation Engine Integration

## Objective

Connect the validated workspace and toolbar execution state to the existing
route-calculation services without blocking the Qt user interface.

## Execution flow

```text
Start (F5)
  → MainWindow creates CalculationJob
  → CalculationJobBuilder reads Excel/CSV rows
  → CalculationExecutionCoordinator creates QThread
  → CalculationWorker runs BatchCalculationService
  → progress/completed/stopped/failed signals return to MainWindow
```

## Supported input

- `.xlsx`
- `.xlsm`
- `.csv`

Rows without a complete origin and destination are skipped. Route options and
travel mode are copied from the validated workspace configuration into each
`RouteRequest`.

## Toolbar behavior

- **Start (F5):** starts the background calculation.
- **Pause/Resume (F6):** cooperatively pauses between rows.
- **Stop (Shift+F5):** requests cancellation between rows and retains results
  already calculated in memory.

## Deliberate boundary

This sprint calculates routes and returns in-memory `RouteResult` objects. It
does not write results back into the workbook. Result persistence belongs to
the following Result Writer sprint.
