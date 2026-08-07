# Sprint 2.6.1-C/D — Semantic Summary & Live Progress

## Changes

- Batch Summary uses semantic colors:
  - Successful: green
  - Failed: red
  - Skipped: yellow
  - Invalid: orange
  - Retried: blue
- Summary appears immediately after Start with zeroed counters.
- Summary updates continuously from `ProgressSnapshot` while the batch runs.
- Final `BatchSummary` still replaces the live counters at Completed or Stopped.
- `ProgressSnapshot` and `BatchProgressTracker` now track invalid and retried counts separately.
- Resume initialization preserves done, failed, skipped, invalid and retry counters.

## Version

`1.2.0-rc15`
