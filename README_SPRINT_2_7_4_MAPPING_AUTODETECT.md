# Sprint 2.7.4 — Result-column auto-detection polish

## Detection priority

1. Header text match.
   - Result distance: `distance`, `km`, `kilomet`, `kilometer`, `kilometre`,
     `khoảng cách`, `quãng đường`, `kết quả`, `result distance`.
   - Result duration: `duration`, `time`, `travel time`, `thời gian`,
     `thời gian di chuyển`, `result duration`.
2. If one or both result columns are still unresolved, use worksheet preview data.
   Candidate columns exclude already-selected Origin/Destination/result roles.
   Columns are ranked by:
   - highest blank-cell count first;
   - left-most column first when blank counts tie.
3. First available ranked candidate becomes Result distance, second becomes
   Result duration.
4. If preview data is unavailable or there are not enough candidates, the
   unresolved selector remains `Select column…` for manual selection.

Header detection always wins over blank-data fallback.
