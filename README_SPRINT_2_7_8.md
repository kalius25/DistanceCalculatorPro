# Sprint 2.7.8 — Final Packaging & Build Smoke

## Goal

Create a repeatable Windows release-candidate build for `1.2.0-rc25` and
validate that the packaged application contains its required UI resources.

## Added

- `python -m app` desktop entry point through `app/__main__.py`.
- `DistanceCalculatorPro.spec` for a one-folder PyInstaller Windows build.
- Frozen-aware ResourceManager support for PyInstaller `_MEIPASS`.
- Required Light/Dark QSS, application icon and splash resources in the build.
- `scripts/build_rc.ps1` for clean build + packaging smoke validation.
- `python -m app.release.package_smoke` build validator.
- PyInstaller promoted to an explicit packaging dependency.
- Full unit tests for build validation and frozen resource resolution.

## Windows build

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_rc.ps1
```

Expected output:

```text
Packaging smoke: PASS
Build PASS: dist/DistanceCalculatorPro
```

After this passes, manually launch
`dist/DistanceCalculatorPro/DistanceCalculatorPro.exe` and perform the final
GUI smoke flow before promoting the version to `1.2.0`.
