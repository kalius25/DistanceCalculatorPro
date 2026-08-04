# Sprint 2.5.1-B1 — GUI Smoke Harness & Happy Path

Adds a deterministic Qt GUI smoke harness that validates the release happy path without Playwright, Chromium, Google Maps, or network access.

## Scope

- Scripted Qt execution coordinator.
- Workbook selection and inspection setup.
- Preflight pass.
- Start action and calculation job creation.
- Progress, metrics, summary, and completion signals.
- Final IDLE state and status-bar verification.
- JSON smoke-report writer.
- `gui_smoke` pytest marker.

## Commands

```powershell
pytest tests\gui_smoke -m gui_smoke -vv
pytest tests\gui_smoke -m "gui_smoke and smoke" -vv
```

Version: `1.2.0-rc6`
