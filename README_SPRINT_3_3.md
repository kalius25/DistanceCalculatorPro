# Sprint 3.3 — OpenStreetMap URL Builder + Engine

## Goal

Add the OpenStreetMap web URL contract and Playwright navigation engine while
keeping result parsing and real batch execution disabled until Sprint 3.4.

## URL contract

Driving:

`https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route=<lat>,<lon>;<lat>,<lon>`

Walking:

`engine=fossgis_osrm_foot`

Coordinates remain in OpenStreetMap's `latitude,longitude` format. Whitespace
is removed and latitude/longitude ranges are validated.

## Engine foundation

`OpenStreetMapEngine.navigate()`:

- builds the complete directions URL;
- navigates with Playwright using `domcontentloaded`;
- emits navigation start/completed diagnostics;
- wraps Playwright timeout/browser failures as `EngineException`.

## Provider readiness after Sprint 3.3

- Google Maps: engine ready + calculation enabled.
- Bing Maps: engine ready + calculation disabled pending Sprint 3.4 parser.
- OpenStreetMap: engine ready + calculation disabled pending Sprint 3.4 parser.

## Non-goals

- OpenStreetMap DOM locator.
- OpenStreetMap Distance/Duration parser.
- OpenStreetMap `BaseProvider` execution implementation.
- Real OSM workbook batch calculation.
- Avoid toll/highway/ferry options for OSM.

Sprint 3.4 can now focus on provider-specific parsing/extraction and activation.
