# Sprint 2.6.3-A1 — Virtual Worksheet Data Source

Introduces the memory-bounded data-source layer required by the upcoming virtual Data Preview.

## Added

- `VirtualWorksheetDataSource` protocol.
- `OpenPyXLVirtualWorksheetDataSource` for XLSX/XLSM worksheets.
- `CsvVirtualWorksheetDataSource` for CSV files.
- `VirtualWorksheetDataSourceFactory` for format selection.
- Bounded `read_rows(start, count)` access with normalized cell widths.
- Explicit source lifecycle (`close`) and range validation.

## Semantics

`row_count` represents data rows after the header row. `headers` represents row 1. No full worksheet row collection is retained in memory.

## Next

Sprint 2.6.3-A2 will connect this source to a lazy `ExcelTableModel` with block caching.
