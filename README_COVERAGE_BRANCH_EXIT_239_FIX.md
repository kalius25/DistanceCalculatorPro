# Coverage branch fix: home_page.py 239->exit

- Baseline: Sprint 2.6.5 B + coverage line 733 fix.
- Production code changes: none.
- Test-only change: `tests/presentation/test_home_page.py`.
- Existing pre-widget safety test now calls `HomePage.release_resources()` on an object without `_preview_model`, covering the false path from line 239 directly to function exit.
- Static compile check: PASS (`python -m compileall -q app tests`).
