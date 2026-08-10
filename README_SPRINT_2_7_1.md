# Sprint 2.7.1 — Recent Workbooks UX Polish

## Changes

- Renamed the legacy recent-file placeholder handler to the real `open recent` flow.
- Recent workbook actions continue to use the same validated workbook selection path as Browse/Open.
- If a recent workbook was moved or deleted, the app now removes the stale path from persisted history automatically.
- Both the Recent Files menu and Home-page Recent Workbooks list refresh immediately after stale cleanup.
- The status bar reports that the recent workbook is unavailable, and the warning explains that the stale entry was removed.
- Added SettingsManager support for removing one recent file without clearing the entire history.

## Roadmap

This begins Sprint 2.7 UX Polish after the Sprint 2.6.5 production-QA baseline.
The next milestone remains v1.2.0 Stable after completion of the 2.7 polish items.
