# Sprint 2.7.9 — Bundled Chromium Final

This revision removes the temporary Chromium-validation bypass from executable
smoke. The automated EXE smoke now follows the same startup browser validation
as a user double-clicking the packaged application.

Build sequence:

1. Install Playwright Chromium.
2. Stage the exact Playwright Chromium executable directory.
3. Bundle it under `_internal/app/browser/chromium`.
4. Packaging smoke requires `chrome.exe`.
5. StartupValidator resolves bundled Chromium.
6. BrowserManager launches that exact executable.
7. Real packaged EXE startup/shutdown smoke must pass without bypassing browser
   validation.

Source runs still fall back to the normal Playwright-managed browser cache.
