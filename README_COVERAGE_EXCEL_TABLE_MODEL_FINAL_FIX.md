# Coverage fix — ExcelTableModel

Target report before patch:

`app/models/excel_table_model.py 155 1 64 3 98% 107, 117->exit, 134->exit`

## Test-only changes

- Extended `test_status_counts_track_sparse_status_transitions` so two rows share `RUNNING`, then one transitions to `SUCCESS`. This covers line 107 (`remaining > 0`) and preserves the existing zero-count removal path.
- Added `test_status_updates_without_visible_status_column` using `show_status_column=False`. This covers the no-signal exit paths after `set_row_status()` and `reset_row_statuses()` corresponding to the remaining `->exit` arcs.
- No production code changed.
- `python -m compileall -q app tests` passes in the sandbox.
