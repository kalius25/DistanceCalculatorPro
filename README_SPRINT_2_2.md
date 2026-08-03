# Sprint 2.2 — Google Maps Smart Recovery

This sprint adds browser health checks and recovery orchestration around the
shared Playwright browser used by GoogleWebProvider.

## Recovery behavior

- Check browser health before each route page is created.
- Replace the page naturally on navigation timeout; the batch retry attempt
  receives a fresh page while retaining the shared browser.
- Restart the shared browser when Playwright reports a closed target,
  disconnected browser, or closed browser/context.
- Record page creation, page failures, timeouts, browser restarts, and recovery
  failures.
- Emit developer diagnostic events when browser tracing is enabled.

## Events

- `RECOVERY_STARTED`
- `PAGE_RECREATED`
- `BROWSER_RESTARTED`
- `RECOVERY_SUCCEEDED`
- `RECOVERY_EXHAUSTED`

## Version

`1.2.0-alpha27`
