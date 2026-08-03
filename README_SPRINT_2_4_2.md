# Sprint 2.4.2 — File Lock Recovery & Safe Output Handling

## Included

- Atomic sibling-temp save for XLSX, XLSM and CSV.
- Existing output is replaced only after a successful temp save.
- Temporary files are removed when save/replace fails.
- `OutputWriteError` preserves destination, operation and reason.
- Writable-directory preflight before each flush.
- Output path policy avoids `.result.result` names.
- Worker emits a structured output-write failure signal.
- GUI offers Retry, Save As and Cancel.
- Retry can rerun the last job with an alternate output path.

## Version

`1.2.0-rc2`
