# Sprint 1A.2-T1 — Presentation Test Foundation

## Scope

This increment adds focused unit tests for independent presentation components:

- `AppMetadata`
- `ResourceManager`
- `SettingsManager`
- `ThemeManager`
- `ExceptionHandler`
- `SplashScreen`
- `AboutDialog`
- Placeholder pages
- `NavigationPanel`

`MainWindow` and `app.py` remain in Sprint 1A.2-T2.

## Headless Qt

The test environment sets `QT_QPA_PLATFORM=offscreen` before Qt is imported.
This keeps widget tests deterministic in local development and CI.

## T1 verification

```powershell
pytest tests/presentation/test_app_metadata.py `
  tests/presentation/test_resource_manager.py `
  tests/presentation/test_settings_manager.py `
  tests/presentation/test_theme_manager.py `
  tests/presentation/test_exception_handler.py `
  tests/presentation/test_splash_screen.py `
  tests/presentation/test_about_dialog.py `
  tests/presentation/test_navigation_panel.py `
  tests/presentation/test_placeholder_pages.py `
  --no-cov
```

Run the complete project quality gate after Sprint 1A.2-T2 adds coverage for
`MainWindow` and `app.py`.
