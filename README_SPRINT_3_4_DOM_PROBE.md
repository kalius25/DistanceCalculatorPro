# Sprint 3.4 — Live DOM Probe

The first real-route validation established:

- Bing Maps navigation PASS, current guessed selectors all miss.
- OpenStreetMap navigation PASS, `#sidebar_content` exists, but guessed
  `.routing_summary` selectors miss.

This revision does not change production provider locators yet. It upgrades the
live validation harness so the next run captures the real rendered DOM.

## Run

```powershell
python -m scripts.smoke_live_providers
```

or:

```powershell
python -m scripts.smoke_live_providers
```

Run the harness as a module from the project root. This keeps imports
standards-compliant and avoids runtime `sys.path` mutation.

## New diagnostics

Console output now includes:

- interesting body lines containing Distance/Time/km/min/hour terms;
- up to 30 DOM elements whose text looks like route metrics;
- element tag, id, class and role;
- full rendered HTML path.

Artifacts now include:

```text
bing_maps_web.html
bing_maps_web.png
openstreetmap_web.html
openstreetmap_web.png
report.json
```

Send the console sections `Interesting body lines` and `DOM metric probes`.
Those values are sufficient to replace guessed locators with selectors observed
from the live pages.
