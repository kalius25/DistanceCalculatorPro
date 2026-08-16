# Sprint 3.4 — Live Locator Fix

This revision replaces guessed provider selectors with selectors observed from
the real rendered pages captured on 2026-08-15.

## Bing Maps

Observed route cards:

- class prefix `routeResultListItemContainer_`
- duration inside `routeTravelTime_*`
- distance inside `routeDistance_*`

The locator intentionally matches only the stable semantic prefix:

```css
[class*='routeResultListItemContainer_']
```

The parser continues to consume the full card text, which preserves route
title, duration, distance, and route warnings. Before regex extraction the
text is normalized to Unicode NFC because Bing's Vietnamese text is rendered
with decomposed combining marks.

Live sample:

- Route 1: 127.2 km / 2 giờ 46 phút
- Route 2: 176.8 km / 3 giờ 57 phút
- Route 3: 209.3 km / 4 giờ 48 phút

## OpenStreetMap

Observed stable result outputs:

```css
#directions_route_distance
#directions_route_time
```

Live sample:

- Distance: 131 km
- Time: 1:57

OSM parsing now reads these outputs directly rather than parsing the whole
sidebar. `H:MM` duration is normalized to minutes.

## Execution state

Provider execution remains gated until the revised live smoke passes for both
Driving and Walking.
