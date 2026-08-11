# Sprint 2.7.7 — Release Candidate Readiness

## Scope

Prepare the completed Sprint 2.7 UX branch for the final v1.2.0 release
candidate quality gate.

## Version consistency

- Runtime/UI version: `1.2.0-rc25`.
- Python package version: `1.2.0rc25` (PEP 440 form).
- Runtime source of truth: `app/version.py`.
- `AppMetadata` reads directly from `app.version.__version__`.
- About page now identifies the build as `v1.2 · Release Candidate`.
- Added tests that fail if package and runtime versions drift apart.

## Next gate

After PASS + 100% coverage, perform the final packaging/build smoke pass before
promoting the release candidate to `v1.2.0`.
