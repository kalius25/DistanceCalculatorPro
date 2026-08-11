# DistanceCalculatorPro 1.2.0-rc25 — Final EXE Smoke Checklist

Run these checks against the packaged executable, not `python -m app`.

## Automated gate

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_rc.ps1
```

Required result:

```text
Packaging smoke: PASS
Executable smoke: PASS
Build PASS: dist/DistanceCalculatorPro
```

## Manual GUI smoke

- Launch `dist/DistanceCalculatorPro/DistanceCalculatorPro.exe`.
- Confirm splash appears and MainWindow opens.
- Confirm application icon, Light theme and Dark theme load correctly.
- Confirm native checkboxes display checked/unchecked states correctly.
- Open an XLSX workbook and verify worksheet preview.
- Verify Origin, Destination, Result distance and Result duration mappings.
- Confirm Result distance/duration auto-detection and manual fallback.
- Run a small batch and verify distance + duration are written.
- Stop a batch and verify the result-file dialog reports the saved path.
- Complete a batch and verify the result-file dialog reports the saved path.
- Choose Yes and confirm the result opens with the Windows default app.
- Open the generated `.result.xlsx` as a new input and verify output becomes
  a distinct `.result.result.xlsx`.
- Verify Recent Workbooks on Home, File menu and History stay synchronized.
- Verify Settings Light/Dark theme persistence.
- Verify About shows `1.2.0-rc25`.
- Exit from File > Exit and confirm no duplicate shortcut label appears.
- Relaunch once and confirm clean startup after normal shutdown.

Promote to `1.2.0` only after every item above passes.
