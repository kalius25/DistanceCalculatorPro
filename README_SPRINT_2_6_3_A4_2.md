# Sprint 2.6.3-A4.2 — Preview View Refresh

Version: `1.2.0-rc18`

This sprint completes worksheet-switch UX refresh for the virtual data preview.

- closes and replaces lazy worksheet sources through the model lifecycle
- clears cached lazy blocks when the source changes
- clears preview selection and current index after model changes
- scrolls the preview to the top after a worksheet switch
- refreshes preview titles for virtual, cached, and empty data
- refreshes worksheet headers without `resizeColumnsToContents()`
- preserves the existing lightweight header-based column sizing

No batch-engine, live-status, or auto-scroll processing behavior is changed.
