# Sprint 1B.4 — Column Mapping Workspace

Adds explicit Origin, Destination and Result column mapping to the Workbook Inspector.

- Populates selectors from the active worksheet headers.
- Auto-detects common English and Vietnamese header names.
- Prevents the same column from being assigned to multiple roles.
- Emits `column_mapping_changed` only when the mapping is complete and valid.
- Resets mapping when the workbook or worksheet is cleared.

This sprint configures the job only. It does not start distance calculation.
