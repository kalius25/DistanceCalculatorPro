# Sprint 2.0.2 — Execution Queue

## Goal

Run pending workbook jobs through the state-aware `BatchQueue` while retaining the existing background worker controls.

## Execution flow

```text
CalculationJob
→ CalculationJobBuilder.build_queue()
→ BatchQueue.next_pending()
→ RouteJob: PENDING → RUNNING
→ CalculationService.calculate()
→ RouteJob: DONE or FAILED
→ progress(current, total, RouteJob, RouteResult)
```

## Scope

- Queue state transitions during real execution.
- Pause, resume, and stop checks between jobs.
- Browser lifecycle remains one browser per non-empty batch.
- Successful jobs retain the selected route distance.
- Failed results retain their error message.
- Unexpected exceptions mark the active job failed and propagate to the worker boundary.

## Deferred

- Workbook result writing.
- Automatic retry policy.
- Persistent resume checkpoints.
