# Sprint 2.5.1-A — Headless E2E Harness

The headless E2E harness executes the real workbook reader, row mapper, batch
queue, retry policy, calculation service, incremental result writer, resume
logic, progress tracker, and summary model without launching Qt, Playwright, or
Google Maps.

## Components

- `ScriptedRouteProvider`: deterministic success/failure scripts.
- `HeadlessE2EHarness`: workbook-to-output orchestration.
- `E2ERunReport`: immutable serializable execution report.
- `E2EReportWriter`: timestamped JSON reliability reports.

## Scenarios covered

- Successful CSV/XLSX/XLSM-compatible pipeline.
- Retry after transient provider/network failure.
- Terminal parser/provider failure.
- Resume from an existing result file.
- Stop after a configured number of completed rows.
- JSON smoke report generation.

## Commands

```powershell
pytest tests\e2e -vv
pytest
```

The provider is entirely local and performs no browser or network calls.
