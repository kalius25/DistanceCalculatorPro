
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

## Sprint 1B.1 — Workspace UI

- Replaced the Home placeholder with a real file-selection workspace.
- Added drag-and-drop and native Browse support for XLSX, XLSM, and CSV files.
- Added selected-file and recent-workbook UI states.
- Connected MainWindow Open and Recent Files actions to workspace selection.
- Added validation for missing and unsupported files.
- Added Light/Dark workspace styling and full Presentation tests.
