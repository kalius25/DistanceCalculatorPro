# Sprint 2.5.2.2-B1 — Deterministic Failure Plan & Recovery Runner

This sprint adds deterministic failure scheduling and recovery stability checks.

## Added

- `FailureKind` and immutable failure/recovery result models.
- `FailurePlan` with ordered events and scenario-range validation.
- `RecoveryRunner` with retryable/non-retryable handling, per-cycle cleanup,
  continued execution after failed cycles, and resource-growth policy checks.
- JSON and Markdown recovery reports.
- Pytest marker `failure_injection`.
- Full unit and branch tests for the new stability modules.

## Supported failure kinds

- provider timeout
- parser failure
- browser crash
- output locked
- permission denied
- disk space blocked
- unexpected exception

## Run

```powershell
pytest tests\stability -m failure_injection -vv
```

Version target: `1.2.0-rc9`.
