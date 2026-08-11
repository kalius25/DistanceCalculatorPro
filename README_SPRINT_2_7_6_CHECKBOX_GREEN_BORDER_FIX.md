# Sprint 2.7.6 — Checkbox Green Border / Check-Mark Fix

## Behavior

- Light theme:
  - Enabled checkbox border: green.
  - Hover border: darker green.
  - Disabled border: gray.
  - Checked state no longer overrides the native check-mark rendering.
- Dark theme:
  - Enabled checkbox border: green.
  - Hover border: lighter green.
  - Disabled border: gray.
- All checkbox indicators use a 2 px border for clearer visibility.

The Light-theme check mark is restored by avoiding a custom checked-state
background/image that could mask the native Qt tick.
