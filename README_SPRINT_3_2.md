# Sprint 3.2 — Bing Maps Provider: URL Builder + Navigation Engine

## Goal

Add the Bing Maps web URL contract and browser navigation foundation without
prematurely enabling Bing result calculation before its parser exists.

## URL contract

Driving:

`https://www.bing.com/maps/directions?style=r&rtp=pos.<lat>_<lon>~pos.<lat>_<lon>&mode=d`

Walking uses `mode=w`.

Input coordinates are normalized from `latitude,longitude` to Bing's
`latitude_longitude` form. Whitespace is removed. Existing Bing underscore
coordinate format is accepted. Latitude/longitude values are validated.

## Engine foundation

`BingMapsEngine.navigate()`:

- builds the complete Bing directions URL;
- navigates with Playwright using `domcontentloaded`;
- emits navigation diagnostics;
- wraps Playwright timeout/browser errors as `EngineException`.

The engine deliberately does not parse Distance/Duration in Sprint 3.2.

## Provider readiness

- Google Maps: engine ready + calculation enabled.
- Bing Maps: engine ready + calculation disabled until Sprint 3.4 parser.
- OpenStreetMap: foundation only; engine begins in Sprint 3.3.

This prevents a Bing selection from silently falling through the existing
Google calculation pipeline.

## Non-goals

- Bing DOM locator.
- Bing Distance/Duration parser.
- Bing `BaseProvider` implementation.
- Bing calculation execution in a real batch.
- Bing avoid toll/highway/ferry options.

Those remain scheduled after the navigation contract is stable.
