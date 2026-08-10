# Sprint 2.6.4-B1 — Row Event Contract & Worker Signals

This increment introduces an immutable row-level execution event contract without yet binding those events to HomePage status rendering.

## Added

- `RouteJobEvent` immutable snapshot with worksheet row, zero-based preview row, status, attempt count, retry count, and message.
- `BatchCalculationService.calculate_queue(..., row_event_callback=...)`.
- Row lifecycle events for `RUNNING`, `RETRY`, resumed `RUNNING`, `DONE`, `FAILED`, and `PENDING` when a retry is requeued after stop.
- Worker `row_event` Qt signal and coordinator relay signal.
- Initial worker events for already-terminal queue rows such as `INVALID` and `SKIPPED`.

## Preview row mapping

The contract normalizes the workbook row number to the Data Preview index:

- worksheet row 2 -> preview row 0
- worksheet row 3 -> preview row 1
- worksheet row N -> preview row N - 2

The event is immutable so later mutations of `RouteJob` cannot change already-delivered UI events.

## Deliberately deferred to B2

- MainWindow/HomePage subscription.
- Mapping `RouteJobStatus` to `PreviewRowStatus`.
- Reset-to-Pending on Start.
- Live rendering in the Status column.
- Auto-scroll and current-row highlighting.
