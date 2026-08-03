# Sprint 2.3.1 — Runtime Performance Metrics & Adaptive Page Recycling

- Reuses one healthy Playwright page across route requests in a batch.
- Recycles the page after a configurable request interval.
- Recycles slow or failed pages proactively.
- Tracks request duration, page creation, recycling, failures and slow requests.
- Preserves Smart Recovery and one-browser-per-batch lifecycle.
