# Sprint 2.0.4 — Progress Engine & Runtime Metrics

Adds queue-based runtime metrics: completed/remaining counts, success/failure totals,
elapsed active time, throughput, average processing time and ETA. Pause duration is
excluded from elapsed time and ETA calculations. Metrics are relayed from the worker
through the execution coordinator to the main window status bar.
