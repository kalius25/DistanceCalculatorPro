# Sprint 2.7.9 — Smoke Browser Validation Fix

The real packaged EXE reached `before create_application` and then displayed:

`Chromium: Browser executable is missing. Run: playwright install chromium`

That is valid normal-runtime behavior, but it blocked the automated packaging
startup smoke on a build machine without Playwright Chromium.

## Fix

- Added explicit `DCP_EXECUTABLE_SMOKE=1` only to the executable-smoke runner.
- `StartupValidator.validate()` now accepts `validate_browser=True`.
- Normal application startup keeps `validate_browser=True`.
- Executable smoke uses `validate_browser=False`.
- Configuration validation and writable Logging/Output directory validation
  still run in smoke mode.
- QApplication, packaged resources, theme, MainWindow construction, Qt event
  loop and clean shutdown are still exercised by the real EXE.

Chromium remains required for normal use and for the manual route-calculation
release smoke.
