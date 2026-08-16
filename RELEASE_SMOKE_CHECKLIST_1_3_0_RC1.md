# DistanceCalculatorPro 1.3.0 RC1 — Release Checklist

## Automated quality + package gate

```powershell
black .
ruff check . --fix
black --check .
ruff check .
mypy app
pytest
powershell -ExecutionPolicy Bypass -File scripts/build_rc.ps1
```

Required:

```text
RC release gate: PASS (1.3.0-rc1)
100% coverage
Packaging smoke: PASS
Executable smoke: PASS
Build PASS: dist/DistanceCalculatorPro
```

## Packaged EXE acceptance

Run the executable from:

```text
dist/DistanceCalculatorPro/DistanceCalculatorPro.exe
```

Check:

- [ ] Splash and MainWindow open normally.
- [ ] No Chromium installation prompt.
- [ ] About shows Version 1.3.0-rc1.
- [ ] About shows Release channel: v1.3 · Release Candidate 1.
- [ ] Existing v1.2 settings/configuration load without startup failure.
- [ ] XLSX preview and column auto-detection work.
- [ ] Google Maps Driving writes distance + duration.
- [ ] Google Maps Walking writes distance + duration.
- [ ] Bing Maps Driving writes distance + duration.
- [ ] Bing Maps Walking writes distance + duration.
- [ ] OpenStreetMap Driving writes distance + duration.
- [ ] OpenStreetMap Walking writes distance + duration.
- [ ] Switching Google → Bing → OSM in one app session works.
- [ ] Stop saves the partial result normally.
- [ ] Completed batch saves the result normally.
- [ ] Result-file Yes/No open prompt works.
- [ ] Reopening `.result.xlsx` creates a distinct output.
- [ ] Close/reopen application and run one provider again.
- [ ] No orphan Chromium process remains after normal shutdown.

## Source-level provider acceptance

Before packaging, optionally rerun:

```powershell
python -m scripts.smoke_production_provider_flow
python -m scripts.smoke_production_provider_flow --mode walking
python -m scripts.smoke_gui_provider_acceptance
python -m scripts.smoke_gui_provider_acceptance --mode walking
```

Promote to `1.3.0 / Stable` only after every RC1 item passes.
