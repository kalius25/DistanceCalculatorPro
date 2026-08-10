# Sprint 2.6.5-B — Status Counts & Filter Badges

Version: `1.2.0-rc24`

The Data Preview status filter now shows live counts such as `Failed (3)` and
`Pending (25,000)` without materializing virtual worksheet rows. Counts are
maintained incrementally by `ExcelTableModel`, while Pending remains implicit.

`Active` is the sum of `Running` and `Retried`. Filter labels refresh after
row-status updates, resets, worksheet changes, and workbook replacement.
