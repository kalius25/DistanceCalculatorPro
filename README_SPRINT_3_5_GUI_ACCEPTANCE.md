# Sprint 3.5 — GUI Acceptance Smoke

This is the final acceptance gate for Sprint 3.5. It exercises the real
MainWindow Start action and worker-thread production flow using a temporary
one-row workbook.

## Driving

```powershell
python -m scripts.smoke_gui_provider_acceptance
```

The harness runs Bing Maps and OpenStreetMap separately. For each provider it:

1. creates a real XLSX workbook;
2. opens it through MainWindow workbook inspection;
3. selects the provider in HomePage;
4. selects Driving;
5. triggers the real Start QAction;
6. waits for the worker-thread completion/failure signal;
7. verifies the generated `.result.xlsx` file;
8. reads `Result distance` and `Result duration`;
9. shuts down the window/coordinator/browser cleanly.

The result-file open prompt is automatically answered **No** so the smoke does
not launch Excel/WPS.

## Walking

```powershell
python -m scripts.smoke_gui_provider_acceptance --mode walking
```

## Individual provider

```powershell
python -m scripts.smoke_gui_provider_acceptance --provider bing
python -m scripts.smoke_gui_provider_acceptance --provider osm
```

## Expected

```text
GUI acceptance: PASS
Workspace ready: True
Completed signal: True
Failed signal: False
Output exists: True
Result distance: <non-empty>
Result duration: <non-empty>
```

Artifacts:

```text
artifacts/gui-provider-acceptance/YYYYMMDD-HHMMSS/
├── bing_maps_web_driving.xlsx
├── bing_maps_web_driving.result.xlsx
├── openstreetmap_web_driving.xlsx
├── openstreetmap_web_driving.result.xlsx
└── report.json
```

If Driving passes for both providers, repeat Walking. After both modes pass,
Sprint 3.5 can be closed.


## QApplication lifecycle fix

The acceptance harness creates exactly one `QApplication` and one `MainWindow`
per process. Multiple providers are then executed sequentially in that same
application session.

This avoids Qt's singleton error:

```text
RuntimeError: libshiboken: Please destroy the QApplication singleton before
creating a new QApplication instance.
```

It also better matches normal user behavior: open the application once, run
Bing Maps, then run OpenStreetMap without restarting the program.
