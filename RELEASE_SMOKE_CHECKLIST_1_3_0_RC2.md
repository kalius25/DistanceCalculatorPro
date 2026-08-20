# DistanceCalculatorPro 1.3.0 RC2 — Multi-Provider Release Checklist

## Automated quality gate

```powershell
black .
ruff check . --fix
black --check .
ruff check .
mypy app
pytest
```

Expected:

```text
100% coverage
```

## RC build

```powershell
powershell -ExecutionPolicy Bypass -File scripts/build_rc.ps1
```

Expected:

```text
RC release gate: PASS (1.3.0-rc2)
Packaging smoke: PASS
Executable smoke: PASS
Build PASS: dist/DistanceCalculatorPro
```

## Live multi-provider regression

```powershell
powershell -ExecutionPolicy Bypass -File scripts/run_rc_regression.ps1
```

The GUI regression runs one application session and nine route scenarios:

```text
Google Maps       Driving   Distance + Duration
Google Maps       Walking   Distance + Duration
Bing Maps         Driving   Distance + Duration
Bing Maps         Walking   Distance + Duration
OpenStreetMap     Driving   Distance + Duration
OpenStreetMap     Walking   Distance + Duration
VietBanDo         Driving   Distance; Duration blank
VietBanDo         Truck     Distance; Duration blank
VietBanDo         Walking   Distance; Duration blank
```

Required final line:

```text
Regression summary: 9/9 PASS
RC2 live regression: PASS
```

After RC2 passes, perform the packaged EXE manual acceptance before promoting
to `1.3.0 / Stable`.
