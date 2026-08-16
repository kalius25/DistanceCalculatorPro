# Sprint 3.5 — Enable Bing Maps + OpenStreetMap Production Flow

## Production flow

The selected workspace provider now flows through the full batch pipeline:

```text
HomePage
  -> WorkspaceConfiguration.provider_configuration.provider
  -> RowMapper metadata["provider"]
  -> RouteRequest.metadata["provider"]
  -> CalculationService
  -> ProviderRouter
  -> GoogleWebProvider / BingWebProvider / OpenStreetMapWebProvider
  -> provider-specific Engine.find_routes()
  -> RouteResult
  -> best route
  -> Result distance + Result duration
```

## Provider availability

All three providers are now execution-enabled:

- Google Maps Web
- Bing Maps
- OpenStreetMap

Bing Maps and OpenStreetMap still disable unsupported Avoid route options in
the UI according to their provider catalog capabilities.

## Resource model

The three provider wrappers share one BrowserManager. ProviderRouter starts
only the provider actually selected by the request, so a normal workbook batch
does not open multiple browser runtimes.

## Sprint gate

Before closing Sprint 3.5:

1. black PASS
2. ruff PASS
3. mypy app PASS
4. pytest PASS
5. statement + branch coverage 100%
6. GUI real workbook smoke using Bing
7. GUI real workbook smoke using OpenStreetMap
8. verify Distance and Duration are written to the selected output columns
