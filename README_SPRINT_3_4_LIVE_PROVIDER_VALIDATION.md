# Sprint 3.4 — Live Provider Validation

Automated tests are already PASS with 100% statement and branch coverage.
Before enabling Bing Maps or OpenStreetMap in production batch execution, run
a real-browser validation against the current provider web pages.

## Run both providers

```powershell
python -m scripts.smoke_live_providers
```

The browser is visible by default. This is intentional so consent banners,
redirects, provider errors, and actual route cards can be inspected.

## Run individually

```powershell
python -m scripts.smoke_live_providers --provider bing
python -m scripts.smoke_live_providers --provider osm
```

Walking mode:

```powershell
python -m scripts.smoke_live_providers --provider all --mode walking
```

Headless mode is available after visible-browser validation:

```powershell
python -m scripts.smoke_live_providers --headless
```

## Output

Each run creates:

```text
artifacts/live-provider-validation/YYYYMMDD-HHMMSS/
├── bing_maps_web.png
├── openstreetmap_web.png
└── report.json
```

The JSON report records:

- generated directions URL;
- navigation PASS/FAIL;
- current engine extraction PASS/FAIL;
- parsed route count;
- candidate DOM selector counts;
- how many candidates contain parseable Distance + Duration;
- text samples and a body excerpt;
- error text when extraction fails.

## Activation rule

Do not set `execution_enabled=True` merely because unit tests pass.

A provider can be activated only after its live report shows:

1. navigation PASS;
2. at least one stable result container;
3. Distance parsed correctly;
4. Duration parsed correctly;
5. Driving real-route smoke PASS;
6. Walking real-route smoke PASS.

If a provider fails, send `report.json` plus the corresponding screenshot.
That gives enough information to correct its locator without guessing DOM
selectors.
