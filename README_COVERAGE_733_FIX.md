# Coverage fix: home_page.py line 733

- Target: `HomePage.preview_status_counts` property.
- Change: extend `test_preview_status_filter_badges_track_live_counts` to assert the property snapshot.
- Production code changed: no.
- Static validation: `python -m compileall -q app tests` passes.
- GUI pytest could not be executed in the sandbox because `PySide6` is not installed here.
- Expected effect in the project CI/dev environment: line 733/return path for `preview_status_counts` becomes covered.
