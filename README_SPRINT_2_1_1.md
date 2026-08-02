# Sprint 2.1.1 — Retry Framework

## Scope

This sprint adds service-layer retry handling for transient route failures.
The presentation layer remains unchanged.

## Runtime behavior

- Each `RouteJob` records attempt count, retry count, last error, start time,
  and finish time.
- Retryable failures use exponential backoff with a configurable cap.
- Parser and validation failures are terminal and are not retried.
- Progress is emitted once per completed job, not once per attempt.
- Pause and stop controls remain active while waiting for a retry.
- A stop request during backoff returns the job to `PENDING` for a later run.

## Defaults

- Maximum attempts: 3
- Initial retry delay: 2 seconds
- Backoff multiplier: 2
- Maximum retry delay: 30 seconds

## Quality gate

Run:

```powershell
ruff check .
black --check .
mypy app
pytest
```
