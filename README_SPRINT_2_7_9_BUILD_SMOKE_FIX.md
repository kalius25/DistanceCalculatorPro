# Sprint 2.7.9 — Windows Build Smoke Fix

Observed real PyInstaller output showed two separate issues.

1. PyInstaller one-folder builds place bundled data under `_internal`.
   Packaging smoke now validates `_internal/app/presentation/...`.
2. PowerShell `$ErrorActionPreference = "Stop"` does not automatically turn
   every non-zero native-process exit code into a terminating error.
   `build_rc.ps1` now checks `$LASTEXITCODE` after every Python command.
3. Executable smoke now writes startup-stage markers to
   `dcp-smoke-status.txt`. If the EXE times out, the error reports the last
   startup stage reached so the next fix can target the actual hang.

The Windows DLL warnings remain build warnings; the PyInstaller build itself
completed successfully in the supplied log.
