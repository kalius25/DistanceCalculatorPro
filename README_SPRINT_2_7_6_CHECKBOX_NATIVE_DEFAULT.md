# Sprint 2.7.6 — Restore Native Checkbox Rendering

All custom QSS rules for `QCheckBox::indicator` have been removed from both
Light and Dark themes.

Checkbox square, checked mark, hover and disabled rendering are now delegated
to the native Qt/platform style. This avoids custom stylesheet rules hiding or
replacing the normal check mark.

No checkbox behavior or business logic was changed.
