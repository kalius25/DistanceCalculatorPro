# Sprint 1A.2 — UI Foundation Polish

**Version:** 1.2.0-alpha2  
**Status:** Ready for local verification

## Goal

Polish the Presentation Foundation without adding business behavior or changing
Business Layer architecture.

## Implemented

- Application SVG icon and startup splash screen.
- Centralized application, splash, style, and icon resource paths.
- QtAwesome icons for primary toolbar actions.
- Exclusive Light/Dark theme actions.
- Refined Light and Dark QSS for menu, navigation, toolbar, status bar,
  dialogs, buttons, and tooltips.
- Keyboard shortcuts:
  - `Ctrl+O`: Open Excel placeholder.
  - `F5`: Start placeholder.
  - `F6`: Pause placeholder.
  - `Shift+F5`: Stop placeholder.
  - `Ctrl+,`: Settings.
  - `Ctrl+1` through `Ctrl+4`: Page navigation.
- Persistent toolbar visibility.
- Recent Files menu infrastructure with empty state and clear command.
- Improved status bar page feedback.
- Improved About dialog.
- Version advanced to `1.2.0-alpha2`.

## Architecture Boundary

This Sprint does not:

- Read Excel.
- Call Controller, Service, Provider, or Engine.
- Calculate distance.
- Add worker threads.
- Add Business Layer behavior.

## Dependency Status

No new dependency was added. Sprint 1A.2 uses `qtawesome`, which was already
present in `requirements.txt`.

## Run

```powershell
python -m app.presentation.app
```

## Local Quality Gate

```powershell
ruff check app tests
black --check app tests
mypy app
pytest
```
