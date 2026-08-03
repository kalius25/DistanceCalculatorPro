# Sprint 2.3.3 — Diagnostics Retention & Batch Benchmark Foundation

## Diagnostics retention

Diagnostic HTML, screenshot and JSON artifacts are now governed by one retention
policy across the complete diagnostics directory. The default limits are 500 files
and 512 MiB. Oldest artifacts are deleted first whenever either limit is exceeded.
Runtime counters expose created/deleted file counts, byte totals and current usage.

## Synthetic benchmark foundation

`app.benchmarks` provides a provider-free benchmark runner with separate timing for
calculation, pacing, autosave and overhead. Results can be persisted as JSON.

Run the standard scenarios with:

```powershell
python -m benchmarks.batch_runtime
```

The script executes synthetic 100, 1,000 and 10,000-job runs and writes a JSON
report below `logs/benchmarks` without calling Google Maps.
