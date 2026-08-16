# Sprint 3.4 — Bing Maps + OpenStreetMap Result Parser / Extraction

## Scope

This sprint adds provider-specific result locators, parsers, and engine
`find_routes()` extraction for Bing Maps and OpenStreetMap.

The parsers normalize web text into the existing `RouteOption` model:

- distance text + canonical kilometers;
- duration text + canonical minutes;
- route summary when available;
- toll/ferry/highway hints when exposed by provider text;
- raw provider/text metadata for diagnostics.

## Reliability boundary

DOM selectors are centralized in:

- `app/engines/bing_maps_locator.py`
- `app/engines/openstreetmap_locator.py`

This keeps provider DOM churn out of parser and execution logic.

## Execution gate

`execution_enabled` remains `False` for Bing Maps and OpenStreetMap in this
sprint. Parser/extraction code must first pass automated tests and then be
validated against live provider pages before provider execution is activated.
This prevents an unverified DOM selector from becoming a production batch
path.

## Live validation note

OpenStreetMap's current directions page exposes Distance and Time fields in
the directions UI. Bing Maps officially documents route distance and travel
duration as route outputs, but the public web application's DOM is not a
stable API contract. Real-browser smoke validation is therefore required
before activation.
