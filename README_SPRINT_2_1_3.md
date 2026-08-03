# Sprint 2.1.3 — Retry Failed Only & Batch Summary

## Delivered

- `BatchQueue.failed_only()` creates an isolated queue containing only failed jobs.
- The execution coordinator retains the latest failed-only queue and can start it with `retry_failed()`.
- The toolbar exposes **Retry Failed** only when the previous summary contains failures.
- Retry-failed runs resume from the existing `.result` workbook so successful values are preserved.
- `BatchSummary` records totals, successes, failures, skipped and invalid rows, resumed rows, retry counts, elapsed time, throughput, output file and stop state.
- `BatchSummaryWriter` writes timestamped JSON reports under `logs/batch/`.
- The status bar shows a compact completion summary.

## Runtime flow

```text
Batch completes
→ summary JSON written
→ failed-only queue retained
→ Retry Failed becomes available
→ existing result workbook reopened
→ only failed rows run again
```
