# Sprint 2.7.9 — Bundled Chromium Runtime

The Windows RC is now self-contained for browser runtime.

## Build flow

1. `python -m playwright install chromium`
2. Resolve the exact Chromium executable Playwright uses.
3. Copy that executable directory to `build/bundled-browser/chromium`.
4. PyInstaller bundles it under `_internal/app/browser/chromium`.
5. Packaging smoke requires `_internal/app/browser/chromium/chrome.exe`.

## Runtime

`resolve_browser_executable()` uses:

1. Bundled `_MEIPASS/app/browser/chromium/chrome.exe`.
2. Playwright-managed Chromium as fallback when running from source.

`BrowserManager` explicitly passes that path to
`playwright.chromium.launch(executable_path=...)`.

Normal EXE users therefore do not need to run `playwright install chromium`.
