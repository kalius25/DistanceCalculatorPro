# Sprint 2.7.10 — Stable Release Promotion

## Scope

Promote the validated `1.2.0-rc25` baseline to `1.2.0` Stable without adding
new product functionality.

## Changes

- Runtime/UI version promoted from `1.2.0-rc25` to `1.2.0`.
- Python package version promoted from `1.2.0rc25` to `1.2.0`.
- About page release channel changed from Release Candidate to Stable.
- Added a Stable metadata gate that blocks packaging if runtime and package
  versions are not exactly `1.2.0`.
- Added `scripts/build_release.ps1` using the proven bundled-Chromium,
  PyInstaller, packaging-smoke and executable-smoke pipeline.
- Added the final Stable manual release checklist.
- No route-calculation, workbook, UI workflow or browser-runtime behavior was
  changed in this promotion.

## Required final gate

1. Pre-commit / lint / type checks PASS.
2. Tests PASS.
3. Statement and branch coverage remain 100%.
4. `scripts/build_release.ps1` PASS.
5. Manual Stable checklist PASS.
6. Tag/release as `v1.2.0`.
