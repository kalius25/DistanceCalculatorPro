# Sprint 2.0.1 — Read Workbook

This sprint introduces the reusable `app.batch` domain package.

## Pipeline

`WorkbookReader -> RowMapper -> RowValidator -> QueueBuilder -> BatchQueue`

## Key decisions

- Excel and CSV rows are streamed instead of retained in memory.
- Every source row becomes a `RouteJob`, including skipped and invalid rows.
- Browser execution is not part of this sprint.
- `CalculationJobBuilder` delegates workbook reading to the new batch pipeline.
- Same-origin and destination rows are completed locally with `0 km`.
