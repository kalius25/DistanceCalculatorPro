# DistanceCalculatorPro 1.2.0 — Stable Release Checklist

Run these checks against the packaged executable, not `python -m app`.

## Automated Stable gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_release.ps1
```

Required result:

```text
Stable release gate: PASS (1.2.0)
Packaging smoke: PASS
Executable smoke: PASS
Stable Build PASS: dist/DistanceCalculatorPro
```

## Manual GUI smoke

- [ ] Launch `dist/DistanceCalculatorPro/DistanceCalculatorPro.exe`.
- [ ] Confirm splash appears and MainWindow opens.
- [ ] Confirm no Playwright/Chromium installation prompt appears.
- [ ] Confirm application icon, Light theme and Dark theme load correctly.
- [ ] Confirm native checkboxes display checked/unchecked states correctly.
- [ ] Open an XLSX workbook and verify worksheet preview.
- [ ] Verify Origin, Destination, Result distance and Result duration mappings.
- [ ] Confirm distance/duration auto-detection and manual fallback.
- [ ] Run a small real batch and verify distance + duration are written.
- [ ] Stop a batch and verify the saved-result dialog and path.
- [ ] Complete a batch and verify the saved-result dialog and path.
- [ ] Choose Yes and confirm the result opens with the Windows default app.
- [ ] Reopen a `.result.xlsx` and verify output uses `.result.result.xlsx`.
- [ ] Verify Recent Workbooks stay synchronized across the UI.
- [ ] Verify Light/Dark theme persistence.
- [ ] Verify About shows Version 1.2.0 and Release channel: v1.2 · Stable.
- [ ] Exit from File > Exit and confirm no duplicate shortcut label appears.
- [ ] Relaunch once and confirm clean startup after normal shutdown.

Release `v1.2.0` only after every item above passes.
