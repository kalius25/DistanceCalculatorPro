# Sprint 3.7B — VietBanDo GUI Diagnostic Fix

The previous GUI acceptance harness could incorrectly report PASS when the
distance cell contained an error string such as:

```text
ERROR: VietBanDo browser operation failed.
```

This package fixes the acceptance condition:

- blank distance -> FAIL
- `ERROR:` distance -> FAIL
- real distance + blank duration -> PASS

When the GUI run fails, the harness now prints the original `RouteResult`
details, including:

- provider
- error code
- error
- context
- exception type
- underlying `EngineException.cause`

Run:

```powershell
python -m scripts.smoke_vietbando_gui_acceptance --mode driving
```

If it fails, copy the lines beginning with `RouteResult[...]`, especially the
`cause:` line. That cause identifies the exact Playwright/QThread failure and
is the basis for the production fix.
