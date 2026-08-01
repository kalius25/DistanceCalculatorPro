# Sprint 1E.2-T1 — Diagnostics Test Completion

This test-completion sprint restores the 100% coverage target after the
Developer Diagnostics Framework was introduced.

## Scope

- Build a genuinely ready workbook workspace before exercising the execution
  coordinator from `MainWindow`.
- Cover independent HTML, screenshot, and JSON diagnostics settings.
- Cover safe diagnostic filename sanitization and fallback naming.
- Cover Google Maps failure capture for open, closed, and invalid pages.
- Cover parser-to-diagnostics route forwarding.
- Cover provider page cleanup when the page is already closed or raises a
  Playwright cleanup error.

No production behaviour or coverage threshold is changed.
