## 1.2.0-alpha7 — Workspace Focus Mode

- Removed the duplicated About This Sheet panel.
- Moved preview-row selection beside the worksheet selector.
- Added 20, 50, 100, 200 and 500 row preview options.
- Added Hide/Show file panels to maximize preview height.
- Increased bounded reader preview capacity to 500 data rows.


## Sprint 1A.2-T1 — Presentation Test Foundation

### Added

- Headless Qt test environment for Presentation Layer tests.
- Unit tests for metadata, resources, settings, themes and exception handling.
- Widget tests for splash screen, About dialog, navigation and placeholder pages.
- Sprint verification guide in `docs/README_SPRINT_1A2_T1.md`.

# Changelog

All notable changes to DistanceCalculatorPro are documented in this file.

## [1.2.0-alpha2] — Sprint 1A.2

### Added

- Application SVG icon.
- Startup splash screen.
- Toolbar action icons.
- Page navigation shortcuts.
- Recent Files menu infrastructure.
- Persistent toolbar visibility.
- Sprint 1A.2 documentation.

### Changed

- Refined Light and Dark themes.
- Improved About dialog.
- Improved status bar page feedback.
- Updated presentation version to `1.2.0-alpha2`.

### Architecture

- No Business Layer changes.
- No new dependency.

## Sprint 1A.2-T2 — Application Shell Test

### Added

- Comprehensive `MainWindow` tests for navigation, menus, toolbar, status bar,
  themes, adaptive icons, recent files, dialogs, placeholders, persistence,
  and close lifecycle.
- Composition-root tests for `create_application()` and `main()`.
- Coverage for normal and exceptional Qt event-loop cleanup.
- Sprint documentation in `docs/README_SPRINT_1A2_T2.md`.

### Changed

- Marked the conventional module launcher guard as excluded from coverage;
  `main()` itself remains fully tested.

## 1.2.0-alpha4 — Sprint 1B.2

- Added immutable workbook and worksheet metadata models.
- Added reader abstraction with streaming CSV and read-only OpenPyXL implementations.
- Added WorkbookInspectorService and composition-root wiring.
- Added Workbook Inspector UI with sheet selection, dimensions, headers, size, type, and modified time.
- Added handling for missing, unsupported, empty, and unreadable workbooks.
- Added unit and presentation tests for the new inspection workflow.

## Sprint 1B.2 Test Stability Fix

- Updated the Workspace status expectation to `Inspecting workbook…`.
- Kept `QMimeData` instances alive for synthetic drag-and-drop events.
- Prevented PySide6 6.11 Windows access violations caused by temporary MIME data ownership.

## 1.2.0-alpha5

### Changed
- Redesigned File Workspace into compact selection, recent files, and file information panels.
- Removed the redundant Change button.
- Expanded Workbook Inspector with a bounded 10-row data preview.
- Added sheet summary and About this sheet details.
- Added Clear Recent List action to the workspace.

### Engineering
- Added preview rows to `WorksheetInfo`.
- Excel and CSV readers retain no more than 10 preview rows.
- Added QTableView-based preview rendering.

## 1.2.0-alpha6 — Sprint 1B.3 Data Preview Completion

- Added a 5/10-row preview selector.
- Added bounded, reusable preview rendering for Excel and CSV worksheets.
- Added cell tooltips so long values remain inspectable without widening the table excessively.
- Added content-aware column sizing with minimum and maximum width limits.
- Preserved read-only and bounded-memory workbook inspection.

## 1.2.0-alpha9

- Fixed the empty-workspace header so guidance and status labels keep their top position when file panels are hidden.
- Applied a fixed vertical size policy to the workspace header and its guidance labels.

## 1.2.0-alpha11 — Automatic Focus Mode

- Automatically hides Select Workbook, Recent Workbooks and File Information after workbook inspection completes.
- Keeps the Show file panels control available so users can reopen the source panels.
- Adds presentation coverage for automatic panel collapse and manual restore.

## 1.2.0-alpha10 — Sprint 1B.4

- Added Column Mapping panel to Workbook Inspector.
- Added Origin, Destination and Result selectors.
- Added Vietnamese and English header auto-detection.
- Added mapping validation and tests.

## Sprint 1B.4 Coverage Completion

- Added branch tests for `HomePage.clear_inspection()` before widget construction.
- Added preview coverage for worksheets without detected headers.
- Added safe sheet-change coverage before workbook inspection exists.
- No production behavior or coverage exclusions were changed.
