# Sprint 2.4.1 — Startup & Shutdown Hardening

## Startup validation

Before the Qt shell and logging handlers are initialized, the application now validates:

- browser and Google Maps timeout values;
- browser viewport dimensions;
- logging and output directories can be created and written;
- the Playwright Chromium executable exists.

Startup failures are collected into one actionable message. Chromium installation failures include the command:

```powershell
playwright install chromium
```

The desktop entry point catches `StartupValidationError`, displays a safe critical dialog and exits with code `1` instead of exposing a traceback to the user.

## Safe shutdown

`CalculationExecutionCoordinator.shutdown()` now:

1. requests the active worker to stop;
2. waits up to the configured timeout for its `QThread`;
3. releases the browser lifecycle through the injected callback;
4. remains safe when called more than once.

When a calculation is active, closing the main window asks the user for confirmation. The window remains open if the user cancels or if the worker does not stop within the timeout.

The application entry point performs final cleanup even when the Qt event loop raises:

- main-window runtime shutdown;
- exception-hook restoration;
- logging-handler reset.

## Release milestone

Version: `1.2.0-rc1`
