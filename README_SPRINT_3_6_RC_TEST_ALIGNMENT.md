# Sprint 3.6 — RC test alignment

The Sprint 3.6 branch runs runtime version `1.3.0-rc1`.

Legacy tests that intentionally validate the historical v1.2 Stable gate must
not assume the branch runtime is still v1.2. Those tests now patch
`stable_release_gate.__version__` to `STABLE_VERSION` so the v1.2 gate remains
tested in isolation.

Updated RC expectations:

- `AppMetadata().version == "1.3.0-rc1"`
- About release channel is `v1.3 · Release Candidate 1`
- package `1.3.0rc1` maps to display/runtime `1.3.0-rc1`
- current runtime consistency test expects `1.3.0-rc1`

No production release metadata was reverted.
