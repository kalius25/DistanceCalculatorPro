# Sprint 1C.2 — Provider State Integration

## Scope

Sprint 1C.2 completes provider configuration state management without starting
batch execution.

## Delivered

- Immutable `ColumnMapping`, `ProviderConfiguration`, and
  `WorkspaceConfiguration` presentation models.
- Typed accessors for the current validated configuration.
- Combined workspace readiness derived from both column mapping and provider
  configuration.
- `workspace_configuration_changed` and transition-only
  `workspace_ready_changed` signals.
- Visible guidance for incomplete mapping, incomplete provider configuration,
  and calculation-ready state.
- Presentation and value-object tests for all readiness branches.

## Quality gate

```powershell
ruff check .
black --check .
mypy app
pytest
```
