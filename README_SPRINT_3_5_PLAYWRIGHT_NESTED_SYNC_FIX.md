# Sprint 3.5 — Production Playwright Nested Sync Fix

## Symptom

Selecting Bing Maps or OpenStreetMap in the GUI and pressing Start failed with:

```text
It looks like you are using Playwright Sync API inside the asyncio loop.
Please use the Async API instead.
```

## Root cause

`BrowserManager.start()` started the persistent Playwright Sync runtime first
and only then called `resolve_browser_executable()`.

In a development checkout there is no PyInstaller bundled Chromium path, so
`resolve_browser_executable()` falls back to `playwright_browser_executable()`.
That resolver temporarily enters its own `sync_playwright()` context.

The old call order therefore created nested Playwright Sync contexts:

```text
sync_playwright().start()
    -> resolve_browser_executable()
        -> sync_playwright()
```

Playwright rejects that nesting with the asyncio-loop error message.

## Fix

Resolve the Chromium executable before starting the managed Playwright runtime:

```text
resolve_browser_executable()
    -> temporary resolver Playwright closes
sync_playwright().start()
    -> managed production runtime starts
```

No Async API migration is required.

The fix applies to the shared BrowserManager, so Google Maps, Bing Maps and
OpenStreetMap all use the same safe lifecycle.
