# Sprint 3.5 — Production Provider Smoke

This smoke test validates Bing Maps and OpenStreetMap beyond the provider
engine layer. It uses the same production service chain that sits behind Start:

```text
RouteRequest.metadata["provider"]
    -> CalculationService
    -> ProviderRouter
    -> BingWebProvider / OpenStreetMapWebProvider
    -> BrowserManager
    -> BingMapsEngine / OpenStreetMapEngine
    -> RouteResult.best_route
```

## Driving

From the project root:

```powershell
python -m scripts.smoke_production_provider_flow
```

Expected for both providers:

```text
Calculation: PASS
Routes parsed: >= 1
Distance: <number> km
Duration: <number> minutes
```

## Walking

```powershell
python -m scripts.smoke_production_provider_flow --mode walking
```

## Individual provider

```powershell
python -m scripts.smoke_production_provider_flow --provider bing
python -m scripts.smoke_production_provider_flow --provider osm
```

## Report

Each run writes:

```text
artifacts/production-provider-smoke/YYYYMMDD-HHMMSS/report.json
```

The report records provider identity, travel mode, success, parsed route count,
selected route, distance, duration and error.

## Sprint 3.5 final GUI gate

After this smoke passes:

1. Open a real workbook in the application.
2. Select Bing Maps, press Start, verify Result distance and Result duration.
3. Repeat with OpenStreetMap.
4. Close/reopen the application and repeat one provider to verify clean browser
   shutdown/restart.
