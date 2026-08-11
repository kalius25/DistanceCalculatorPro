# Sprint 2.7.3 — Settings UX Polish

## Scope

Settings is now a real application page instead of a placeholder.

## Changes

- Added Appearance settings with Light / Dark theme selection.
- Added Diagnostics settings for Debug Mode, browser trace, parser diagnostics,
  HTML capture, screenshot capture and parser JSON capture.
- Settings uses the existing SettingsManager and DiagnosticsManager state.
- View/Debug menu actions and the Settings page synchronize in both directions.
- Dependent diagnostics controls are disabled when Debug Mode is off.
- Programmatic state synchronization blocks signals to avoid recursive updates.
- Added pytest-qt coverage for page state, signal emission and MainWindow sync.

## Roadmap

Sprint 2.7 UX Polish continues toward v1.2.0 Stable.
