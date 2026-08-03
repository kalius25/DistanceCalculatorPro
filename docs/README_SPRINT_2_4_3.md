# Sprint 2.4.3 — Large Batch Protection & Resource Preflight

This sprint adds a reusable batch preflight framework before execution starts.

## Checks

- Estimates jobs and output size without loading the workbook into memory again.
- Verifies the output location is writable.
- Verifies available disk space with a configurable safety reserve.
- Warns before very large batches.
- Blocks execution when disk space or output access is insufficient.

## User actions

Blocking failures always show a dialog with **Check Again**, **Choose Another Location**, and **Cancel**. Large-batch warnings provide **Continue**, **Choose Another Location**, and **Cancel**. The status bar retains the blocking reason after the dialog closes.

## Diagnostics

Preflight warnings and blocks are logged as `BATCH_PREFLIGHT_WARNING` and `BATCH_PREFLIGHT_BLOCKED`, including estimated jobs, required bytes, available bytes, output path, and issue codes.
