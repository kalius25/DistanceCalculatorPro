# Sprint 3.7B — VietBanDo Live DOM Probe

This first 3.7B package intentionally does **not** enable VietBanDo production
execution yet.

It adds a live Chromium probe that opens the exact VietBanDo URL contract and
captures the rendered result DOM for:

- Driving (`MODE=2`)
- Truck (`MODE=3`)
- Walking (`MODE=5`)

Run from the project root:

```powershell
python -m scripts.smoke_vietbando_dom
```

Run one mode only:

```powershell
python -m scripts.smoke_vietbando_dom --mode driving
python -m scripts.smoke_vietbando_dom --mode truck
python -m scripts.smoke_vietbando_dom --mode walking
```

Default browser mode is visible. Add `--headless` only if needed.

Artifacts are written under:

```text
artifacts/vietbando-dom-probe/YYYYMMDD-HHMMSS/
```

For each mode the harness writes:

- rendered HTML;
- full-page screenshot;
- body excerpt;
- candidate selector counts/samples;
- DOM elements containing likely distance/time metrics;
- `report.json`.

After running, send the console output or `report.json`. The next 3.7B step
will turn the confirmed DOM structure into VietBanDo Locator + Parser + Engine.
