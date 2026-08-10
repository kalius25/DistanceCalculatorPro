# Sprint 2.6.5 B - Distinct Output + Save Debug Logging Fix

## Behaviour

The selected input workbook is never used as the result destination.

- `A.xlsx` -> `A.result.xlsx`
- `A.result.xlsx` -> `A.result.result.xlsx`
- `A.result.result.xlsx` -> `A.result.result.result.xlsx`

Even an explicit output path equal to the selected source is redirected through `OutputPathPolicy`.

## Save diagnostics

Detailed structured DEBUG events were added for output-path selection, writer creation, source snapshot, writability preflight, temporary file creation, workbook write, atomic replace, and flush completion/failure. Important events include:

- `OUTPUT_PATH_BUILT`
- `RESULT_WRITER_FACTORY_CREATE`
- `EXCEL_WRITER_OPEN_BEGIN` / `EXCEL_WRITER_SOURCE_SNAPSHOT_OK` / `EXCEL_WRITER_OPEN_OK`
- `RESULT_FLUSH_BEGIN` / `RESULT_FLUSH_OK`
- `OUTPUT_WRITABLE_CHECK_BEGIN` / `OUTPUT_WRITABLE_CHECK_OK` / `OUTPUT_WRITABLE_CHECK_FAILED`
- `ATOMIC_CREATE_BEGIN` / `ATOMIC_CREATE_OK`
- `EXCEL_SAVE_TEMP_WRITE_BEGIN` / `EXCEL_SAVE_TEMP_WRITE_OK`
- `ATOMIC_REPLACE_BEGIN` / `ATOMIC_REPLACE_OK` / `ATOMIC_REPLACE_FAILED`
- `EXCEL_SAVE_OK` / `EXCEL_SAVE_OUTPUT_WRITE_FAILED` / `EXCEL_SAVE_IO_FAILED`

The logs include source/output/temp paths, existence flags, file sizes, and exception types/messages where applicable.
