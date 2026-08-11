# Sprint 2.7.9 — Executable Build & Final Smoke

## Automated executable smoke

The packaged EXE is now launched as part of the RC build gate.

`DCP_SMOKE_EXIT_MS` is an internal smoke-only environment variable. When set to
a positive integer, the real Qt application schedules a clean `quit()` after
startup. Normal users never set this variable, so normal runtime behavior is
unchanged.

The smoke verifies that the actual packaged application can initialize,
construct its MainWindow, load packaged resources, enter the Qt event loop and
exit with code 0.

## Build gate

`scripts/build_rc.ps1` now requires:

1. PyInstaller build succeeds.
2. Static package/resource smoke passes.
3. Actual EXE startup/shutdown smoke passes.

A manual RC25 GUI checklist is included in
`RELEASE_SMOKE_CHECKLIST_1_2_0_RC25.md`.
