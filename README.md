# DistanceCalculatorPro

## Features

## Installation

## Build

## Run

## Test
ruff check .
mypy app
pytest
pytest --cov=app --cov-report=term-missing
coverage html

## Project Structure

## Screenshots

## License
## Developer diagnostics

Use the **Debug** menu to enable developer diagnostics while testing Google Maps.
Debug Mode is the master switch. Browser trace, parser diagnostics, HTML,
screenshot and JSON capture can then be enabled independently. Preferences are
stored by QSettings and restored at the next application start. Artifacts are
written below `logs/debug/`.

## Incremental result output

Batch results are written to a sibling `.result` workbook. Excel/XLSM workbooks
remain open for the complete batch and are autosaved every 20 written rows or
30 seconds. CSV output is rewritten at the same autosave checkpoints. The
source file is not overwritten by default.
