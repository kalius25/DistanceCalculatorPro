# Sprint 2.7.5 — Menu & Action UX / Release Readiness

## Changes

- Renamed `Open Excel` to `Open Workbook...` because the application supports
  XLSX, XLSM and CSV inputs.
- Kept the standard Ctrl+O shortcut for Open Workbook.
- File > Exit remains shortcut-free to avoid the duplicate `Exit  Exit` menu
  rendering seen on Windows/Qt.
- Added status-bar descriptions to primary File, View, execution, Settings,
  About, diagnostics-support and navigation actions.
- Navigation actions now expose a consistent `Open the <page> page` status tip.
- Added regression tests for user-visible labels, shortcuts and status tips.

## Roadmap

Sprint 2.7 is now in release-readiness polish toward v1.2.0 Stable.
