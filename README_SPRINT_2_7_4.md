# Sprint 2.7.4 — About UX Polish

## Scope

About is now a real application page instead of the final navigation placeholder.

## Changes

- Replaced the About placeholder with a metadata-backed application information page.
- Shows product name, current version, release channel, organization and product summary.
- Added an About dialog button on the page.
- The page button reuses the existing AboutDialog flow instead of duplicating dialog logic.
- MainWindow now owns the AboutPage instance and injects the same AppMetadata used by the dialog.
- Added pytest-qt coverage for metadata rendering, default metadata and page-to-dialog signal flow.

## Roadmap

Sprint 2.7 UX Polish now has real Home, History, Settings and About pages.
The next milestone remains v1.2.0 Stable after the remaining polish and release-readiness checks.
