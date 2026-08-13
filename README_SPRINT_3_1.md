# Sprint 3.1 — Provider Foundation

## Goal

Prepare DistanceCalculatorPro v1.3 for multiple web routing providers without
changing the proven Google Maps calculation behavior from v1.2.0 Stable.

## Provider catalog

The application now knows three providers:

- Google Maps Web — executable now.
- Bing Maps — foundation visible; execution begins in Sprint 3.2.
- OpenStreetMap — foundation visible; execution begins in Sprint 3.3.

All three declare Driving and Walking as the initial v1.3 travel-mode surface.

## Safety rules

Sprint 3.1 does not execute Bing Maps or OpenStreetMap.

The Home provider selector exposes all three providers so the v1.3 UX and
configuration model can be exercised early. Selecting Bing Maps or
OpenStreetMap marks provider configuration as not ready and disables route
preference checkboxes.

`CalculationJobBuilder` also contains an execution guard. A non-Google
workspace configuration created programmatically cannot silently run through
the existing Google provider.

## Provider capabilities

Provider metadata is centralized in `app/providers/catalog.py` rather than
hard-coded into individual presentation widgets. This is the foundation for
Sprint 3.2 Bing Maps and Sprint 3.3 OpenStreetMap.

Google Maps retains existing toll/highway/ferry option behavior. Bing and OSM
route preferences remain disabled until their provider implementations define
and test those capabilities.

## Non-goals

- No Bing URL builder.
- No Bing parser.
- No OpenStreetMap URL builder.
- No OpenStreetMap parser.
- No provider switching inside the execution dependency tree.
- No performance architecture changes.

Those changes belong to later v1.3/v1.4 roadmap sprints.
