# Sprint 2.6.5-A - Status Filter Bar

Version: `1.2.0-rc23`

Adds a compact status filter to Data Preview without materializing virtual rows. Available filters: All statuses, Active, Success, Failed, Skipped, Invalid, Retried, and Pending. Filtering is implemented with `PreviewStatusFilterProxyModel`, keeping `ExcelTableModel` as the source of truth. Live status updates invalidate the filter incrementally, and current-row focus maps source indexes through the proxy.
