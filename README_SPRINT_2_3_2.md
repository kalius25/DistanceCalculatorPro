# Sprint 2.3.2 — Autosave Optimization & Request Pacing

## Autosave runtime metrics

Every result writer now exposes an immutable autosave snapshot containing:

- completed save count;
- total and last rows saved;
- total, average and maximum save duration.

Flush still occurs only when the writer is dirty, preventing duplicate saves.

## Adaptive request pacing

GoogleWebProvider now uses an adaptive pacer between requests:

- delay increases after failed requests;
- delay decreases after successful requests;
- delay is clamped to configurable minimum and maximum values;
- pacing counters reset at the start of each batch.

The default initial and minimum delay remain zero, preserving current runtime
behaviour until pacing is explicitly configured.
