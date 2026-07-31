# Sprint 1A.2-T2 — Application Shell Test

## Objective

Complete automated tests for the Presentation application shell without
changing its user-facing behavior.

## Scope

### MainWindow

- Initial window structure and state
- Menu bar, toolbar, status bar, and page stack
- Navigation panel and keyboard navigation actions
- Settings-page and About-dialog actions
- Light and dark theme switching
- Adaptive action icon colors
- Empty and populated recent-files menus
- Recent-file placeholder and clear-history action
- Sprint placeholder commands
- Toolbar visibility persistence
- Geometry and window-state restoration
- Geometry and window-state persistence on close
- Defensive sender and invalid-page branches

### Application composition root

- `create_application()` dependency composition
- Qt application metadata and icon setup
- Splash-screen lifecycle
- Settings and saved-theme loading
- Unsupported saved-theme fallback
- Exception-handler installation
- Main-window construction
- Event-loop result propagation
- Cleanup after normal and exceptional event-loop termination

## Test commands

```powershell
pytest tests/presentation/test_main_window.py `
  tests/presentation/test_app.py --no-cov
```

Then run the complete quality gate:

```powershell
ruff check app tests
black --check app tests
mypy app
pytest
```

## Notes

The conventional `if __name__ == "__main__"` launcher guard is excluded from
coverage because it delegates directly to the independently tested `main()`
function. No runtime behavior is changed.
