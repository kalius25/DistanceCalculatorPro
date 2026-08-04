# Sprint 2.5.2.2-A — Stability Harness & Leak Snapshot

Adds deterministic long-running stability primitives without GUI, browser, network,
or Google Maps dependencies.

## Included

- repeated stability scenarios and policies;
- memory, thread, garbage-collector, weak-reference, and file-handle snapshots;
- cleanup and garbage collection between cycles;
- policy violations for memory, thread, weak-reference, and handle growth;
- JSON and Markdown stability reports;
- `stability` and `soak` pytest markers.

## Commands

```powershell
pytest tests\stability -m stability -vv
pytest tests\stability -m soak -vv
```

The default test suite contains only deterministic, fast stability tests. Extended
soak scenarios are opt-in.
