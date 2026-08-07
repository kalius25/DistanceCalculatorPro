# Sprint 2.6.3-A2 — Lazy ExcelTableModel + Block Cache

This step connects the virtual worksheet data source introduced in A1 to the Qt table model.

## Added

- `VirtualTableBlockCache`: bounded LRU cache for row blocks.
- `ExcelTableModel.set_source(source)`: exposes the full worksheet row count without materializing all rows.
- Lazy `data()` access in fixed-size blocks (default 256 rows).
- `invalidate_cache()` for explicit refresh.
- `clear_source()` and automatic closing when a virtual source is replaced or the model returns to in-memory data.
- Backward compatibility with the existing `set_data()` API.

## Not yet changed

- HomePage still uses the existing preview workflow.
- Preview Rows controls are removed in A3, not A2.
- Live row status and auto-scroll remain future work.
