# Sprint 1A.1 — Presentation Infrastructure

## Added

- Centralized `AppMetadata`.
- Centralized `ResourceManager`.
- Persistent `SettingsManager` based on `QSettings`.
- Global `ExceptionHandler` with technical logging and safe UI message.
- Reusable `AboutDialog`.
- Theme persistence.
- Window geometry and toolbar state persistence.
- Composition-root integration with existing configuration and logging systems.

## Run

```powershell
python -m app.presentation.app
```

## Validation

```powershell
ruff check app tests
black --check app tests
mypy app
```
