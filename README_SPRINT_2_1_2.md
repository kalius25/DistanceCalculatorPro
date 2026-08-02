# Sprint 2.1.2 — Resume Batch & Skip Existing Results

## Scope

- Existing non-empty result cells can be preserved when building the batch queue.
- Previous `ERROR:`, `FAILED:` and Vietnamese error values remain pending for retry.
- The workspace option **Skip rows already containing a result** defaults to enabled.
- Disabling the option forces existing rows back into the pending queue.
- Resumed values are not overwritten during the initial writer flush.
- Progress metrics begin with workbook rows that are already terminal.

## Resume rules

| Existing result | Skip enabled | Initial state |
|---|---:|---|
| Empty | Yes/No | `PENDING` |
| Number or numeric km text | Yes | `DONE` |
| Other non-empty text | Yes | `DONE` |
| Previous error text | Yes/No | `PENDING` |
| Any non-empty result | No | `PENDING` |

## Quality gate

Run on Windows:

```powershell
ruff check .
black --check .
mypy app
pytest
```
