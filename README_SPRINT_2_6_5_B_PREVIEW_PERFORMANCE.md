# Sprint 2.6.5 B — Preview Performance Optimization

## Changes

- Removed the live activity text displayed before the Auto-scroll checkbox.
- Added a dedicated execution state signal at the beginning of the status bar:
  `[Ready]`, `[Running]`, `[Paused]`, `[Completed]`, `[Stopped]`.
- Progress detail remains immediately after the state signal, e.g.:
  `[Running] 53/100 - 53% - 12.4 jobs/min - Elapsed 04:16 - ETA 03:47`.
- Removed per-row live activity string construction from `MainWindow._on_row_event()`.
- Removed explicit `PreviewStatusFilterProxyModel.refresh_filter()` calls after every row status update.
  The proxy already has `dynamicSortFilter=True`, and the source model emits `dataChanged`
  for the affected row, allowing Qt to re-evaluate only the changed row.
- Status counts remain incrementally maintained in `ExcelTableModel` (O(1) updates).
- The filter combo now displays a count only for the currently selected filter item.
  Unselected items remain plain labels and are not rewritten on every job update.

## Performance rationale

The status counter itself was not scanning the workbook. `ExcelTableModel` already updates
its `_status_counts` dictionary incrementally. The more expensive operation was forcing a
proxy filter refresh after every job state transition, potentially re-evaluating many rows.
This sprint removes that redundant full refresh and reduces per-job widget updates.
