# Sprint 2.6.3-A4.3 — Workbook Replacement & Cleanup

Version: `1.2.0-rc18`

## Scope

- Release the active virtual worksheet source when inspection is cleared.
- Close the previous worksheet source when a new workbook replaces it.
- Release preview resources when `HomePage` closes.
- Explicitly release HomePage preview resources during successful `MainWindow.closeEvent`.
- Keep resources intact when application close is cancelled or worker shutdown fails.
- Preserve the existing lazy model and block-cache behavior.

## Resource lifecycle

```text
Open workbook A -> virtual source A
Open workbook B -> source A closes -> source B becomes active
Clear inspection -> active source closes -> cache/model reset
Close window -> worker shutdown succeeds -> active source closes -> settings persist
```

## Notes

This sprint does not add prefetching, live row status, auto-scroll, or processing highlights.
