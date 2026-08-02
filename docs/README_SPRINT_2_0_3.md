# Sprint 2.0.3 — Result Writer & Incremental Save

## Output files

The source workbook is never overwritten by default. Results are written beside
it using the following convention:

- `routes.xlsx` → `routes.result.xlsx`
- `routes.xlsm` → `routes.result.xlsm`
- `routes.csv` → `routes.result.csv`

## Lifecycle

One writer remains open for the whole batch. Each terminal route job is written
to its original one-based source row and the mapped result column. The writer
saves after either 20 dirty rows or 30 seconds, whichever occurs first, and
always flushes on completion, stop, or failure.

## Values

- `DONE`: writes the selected route distance in kilometres.
- `FAILED` and `INVALID`: writes an `ERROR: ...` diagnostic message.
- `SKIPPED`: leaves the result cell unchanged.

XLSM input uses `keep_vba=True` so embedded VBA content is preserved.

## Quality gate

```powershell
ruff check .
black --check .
mypy app
pytest
```
