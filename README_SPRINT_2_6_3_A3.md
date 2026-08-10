# Sprint 2.6.3-A3 — Virtual Preview Integration

This sprint connects the virtual worksheet data source and lazy `ExcelTableModel` to the Home workspace.

## Changes

- Removed the `Preview Rows` selector from Workbook Inspector.
- The Data Preview uses `VirtualWorksheetDataSourceFactory` for real XLSX/XLSM/CSV files.
- `ExcelTableModel.rowCount()` exposes all data rows from the selected worksheet.
- Changing worksheet replaces and closes the previous virtual source automatically.
- Clearing workbook inspection clears the model and closes the source.
- The old bounded `WorksheetInfo.preview_rows` remains only as a safe compatibility fallback when a real source file is unavailable.
- Column widths are estimated from header text rather than scanning every row, preserving lazy behavior.

## Scope intentionally deferred

- Live per-row execution status
- Auto-scroll to current processing row
- Status column and incremental result updates

Those are planned for later Sprint 2.6.3 phases.
