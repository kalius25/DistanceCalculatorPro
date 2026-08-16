# Sprint 3.4 — Walking Validation Gate

Driving live validation has already passed for both providers:

- Bing Maps: navigation PASS, extraction PASS, 3 routes.
- OpenStreetMap: navigation PASS, extraction PASS, 1 route.

The final Sprint 3.4 gate is Walking.

## Run both providers in Walking mode

From the project root:

```powershell
python -m scripts.smoke_live_providers --mode walking
```

Expected:

```text
== Bing Maps ==
Navigation: PASS
Engine extraction: PASS
Routes parsed: >= 1

== OpenStreetMap ==
Navigation: PASS
Engine extraction: PASS
Routes parsed: 1
```

## Candidate selectors

The diagnostic candidates now match the DOM observed during the successful
Driving validation.

Bing Maps:

```css
[class*='routeResultListItemContainer_']
[class*='routeResultListItem_']
[class*='routeInfo_']
[id^='routeDistance_']
```

OpenStreetMap:

```css
#directions_route_distance
#directions_route_time
#sidebar_content
```

## Sprint close rule

Sprint 3.4 can be closed when:

1. Full quality gate PASS.
2. Coverage = 100%.
3. Bing Driving PASS.
4. OSM Driving PASS.
5. Bing Walking PASS.
6. OSM Walking PASS.

After that, Sprint 3.5 can enable Bing Maps and OpenStreetMap in the
production calculation flow.
