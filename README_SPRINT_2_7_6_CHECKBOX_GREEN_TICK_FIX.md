# Sprint 2.7.6 — Explicit Green Checkbox Tick

Qt stylesheet borders can replace native checkbox painting, which caused the
native checked mark to disappear. The checked indicator now uses an explicit
SVG check mark.

- Light checked checkbox: green border + green V tick.
- Dark checked checkbox: green border + green V tick.
- Enabled unchecked checkbox: green border.
- Disabled checkbox: gray border.
- The tick is rendered explicitly instead of relying on the platform Qt style.
