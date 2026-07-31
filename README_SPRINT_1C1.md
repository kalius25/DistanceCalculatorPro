# Sprint 1C.1 — Provider Configuration Workspace

## Scope

Adds route-provider configuration to the Workbook Inspector without starting batch execution.

## User interface

- Provider: Google Maps Web
- Travel mode: Driving, Walking, Bicycling, Transit
- Route options: Avoid tolls, Avoid highways, Avoid ferries
- Provider readiness status

## Presentation contract

`HomePage.provider_configuration_changed` emits:

```python
(provider, travel_mode, avoid_tolls, avoid_highways, avoid_ferries)
```

The signal is emitted only when provider and travel mode are valid.

## Quality gate

```powershell
ruff check .
black --check .
mypy app
pytest
```
