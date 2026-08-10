# Sprint 2.6.4-A — Data Preview Row Status Column

Version: `1.2.0-rc19`

This sprint introduces the visual processing-state foundation for the virtual Data Preview grid.

- Adds a leading `Status` column to the HomePage preview grid.
- Pending is implicit, so large worksheets do not allocate one status object per row.
- Supports Pending, Running, Success, Failed, Skipped, Invalid, and Retried states.
- Status changes emit `dataChanged` only for the affected status cell.
- Status state resets when worksheet/source data changes.
- Existing `ExcelTableModel` consumers remain compatible because the status column is opt-in.

Live wiring from batch worker progress to individual rows is intentionally deferred to Sprint 2.6.4-B.
