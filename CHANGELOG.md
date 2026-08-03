
## 1.2.0-alpha29

- Added autosave duration and row-count metrics.
- Added adaptive request pacing with bounded increase/decrease rules.
- Reset pacing state at the beginning of each batch.
- Added tests for autosave metrics and pacing lifecycle.
## 1.2.0-alpha26

- Added Retry Failed Only execution based on the previous failed job queue.
- Added batch summary metrics and timestamped JSON reports.
- Added Retry Failed toolbar action and compact GUI summary.
- Retry-failed execution now resumes from the existing result workbook.


## 1.2.0-alpha25

- Added resumable queue construction from existing workbook results.
- Added the GUI option to skip rows that already contain results.
- Preserved existing result values during incremental writer startup.
- Restored Progress Engine exports and runtime metric relay.

## 1.2.0-alpha24

- Added transient failure retry framework with exponential backoff.
- Added per-job attempt, retry, error, and timing metadata.
- Retry delays honor pause and stop controls without double-counting progress.


## 1.2.0-alpha22 — Sprint 2.0.3 Result Writer & Incremental Save

- Added Excel, XLSM, and CSV result writers with one open document per batch.
- Added safe sibling output files using the `.result` naming convention.
- Added row- and time-based autosave with mandatory final flush.
- Preserved VBA content when loading and saving XLSM workbooks.
- Wrote successful distances and failed/invalid messages to mapped result cells.
- Integrated result persistence with `BatchCalculationService` and the worker.

## 1.2.0-alpha21 — Sprint 2.0.2 Execution Queue

- Execute workbook rows through `BatchQueue` instead of a detached request list.
- Transition route jobs through `PENDING`, `RUNNING`, `DONE`, and `FAILED`.
- Relay progress with the originating `RouteJob` and `RouteResult`.
- Preserve pause, resume, stop, and one-browser-per-batch behavior.
- Keep the request-list API for backward compatibility.

## 1.2.0-alpha16 — Sprint 1E.0

- Added `CalculationJobBuilder` for Excel, XLSM and CSV input.
- Added background `CalculationWorker` and Qt execution coordinator.
- Connected Start, Pause/Resume and Stop to real batch calculation.
- Added cooperative pause and stop callbacks to `BatchCalculationService`.
- Added progress, completion, stopped and failure status handling.
- Result writing remains intentionally deferred to the Result Writer sprint.

## 1.2.0-alpha15 — Sprint 1D.2

- Made MainWindow the single owner of execution orchestration and toolbar state.
- Added the HomePage `workspace_locked` view state and `set_workspace_locked()` API.
- Locked and restored all calculation configuration controls through one view-only API.
- Preserved guarded IDLE/RUNNING/PAUSED transitions and calculation request signals.
- Extended presentation tests for lock state, transitions, toolbar text, and signal emission.

## 1.2.0-alpha14

- Added Sprint 1D.1 Execution Workspace with validated Start/Stop controls.
- Added execution summary and configuration locking while a job is active.
- Added calculation request and stop request signals.

## 1.2.0-alpha13

- Added Sprint 1C.2 provider state integration.
- Added immutable typed workspace configuration models.
- Added combined mapping/provider readiness and signals.
- Added complete readiness-state tests and theme styling.


## 1.2.0-alpha12

- Added Sprint 1C.1 Provider Configuration Workspace.
- Added Google Maps Web provider selection.
- Added travel-mode selection and route avoidance options.
- Added provider readiness validation and presentation signal.
- Added provider configuration tests and theme styling.
## 1.2.0-alpha7 — Workspace Focus Mode

- Removed the duplicated About This Sheet panel.
- Moved preview-row selection beside the worksheet selector.
- Added 20, 50, 100, 200 and 500 row preview options.
- Added Hide/Show file panels to maximize preview height.
- Increased bounded reader preview capacity to 500 data rows.


## Sprint 1A.2-T1 — Presentation Test Foundation

### Added

- Headless Qt test environment for Presentation Layer tests.
- Unit tests for metadata, resources, settings, themes and exception handling.
- Widget tests for splash screen, About dialog, navigation and placeholder pages.
- Sprint verification guide in `docs/README_SPRINT_1A2_T1.md`.

# Changelog

All notable changes to DistanceCalculatorPro are documented in this file.

## [1.2.0-alpha2] — Sprint 1A.2

### Added

- Application SVG icon.
- Startup splash screen.
- Toolbar action icons.
- Page navigation shortcuts.
- Recent Files menu infrastructure.
- Persistent toolbar visibility.
- Sprint 1A.2 documentation.

### Changed

- Refined Light and Dark themes.
- Improved About dialog.
- Improved status bar page feedback.
- Updated presentation version to `1.2.0-alpha2`.

### Architecture

- No Business Layer changes.
- No new dependency.

## Sprint 1A.2-T2 — Application Shell Test

### Added

- Comprehensive `MainWindow` tests for navigation, menus, toolbar, status bar,
  themes, adaptive icons, recent files, dialogs, placeholders, persistence,
  and close lifecycle.
- Composition-root tests for `create_application()` and `main()`.
- Coverage for normal and exceptional Qt event-loop cleanup.
- Sprint documentation in `docs/README_SPRINT_1A2_T2.md`.

### Changed

- Marked the conventional module launcher guard as excluded from coverage;
  `main()` itself remains fully tested.

## 1.2.0-alpha4 — Sprint 1B.2

- Added immutable workbook and worksheet metadata models.
- Added reader abstraction with streaming CSV and read-only OpenPyXL implementations.
- Added WorkbookInspectorService and composition-root wiring.
- Added Workbook Inspector UI with sheet selection, dimensions, headers, size, type, and modified time.
- Added handling for missing, unsupported, empty, and unreadable workbooks.
- Added unit and presentation tests for the new inspection workflow.

## Sprint 1B.2 Test Stability Fix

- Updated the Workspace status expectation to `Inspecting workbook…`.
- Kept `QMimeData` instances alive for synthetic drag-and-drop events.
- Prevented PySide6 6.11 Windows access violations caused by temporary MIME data ownership.

## 1.2.0-alpha5

### Changed
- Redesigned File Workspace into compact selection, recent files, and file information panels.
- Removed the redundant Change button.
- Expanded Workbook Inspector with a bounded 10-row data preview.
- Added sheet summary and About this sheet details.
- Added Clear Recent List action to the workspace.

### Engineering
- Added preview rows to `WorksheetInfo`.
- Excel and CSV readers retain no more than 10 preview rows.
- Added QTableView-based preview rendering.

## 1.2.0-alpha6 — Sprint 1B.3 Data Preview Completion

- Added a 5/10-row preview selector.
- Added bounded, reusable preview rendering for Excel and CSV worksheets.
- Added cell tooltips so long values remain inspectable without widening the table excessively.
- Added content-aware column sizing with minimum and maximum width limits.
- Preserved read-only and bounded-memory workbook inspection.

## 1.2.0-alpha9

- Fixed the empty-workspace header so guidance and status labels keep their top position when file panels are hidden.
- Applied a fixed vertical size policy to the workspace header and its guidance labels.

## 1.2.0-alpha11 — Automatic Focus Mode

- Automatically hides Select Workbook, Recent Workbooks and File Information after workbook inspection completes.
- Keeps the Show file panels control available so users can reopen the source panels.
- Adds presentation coverage for automatic panel collapse and manual restore.

## 1.2.0-alpha10 — Sprint 1B.4

- Added Column Mapping panel to Workbook Inspector.
- Added Origin, Destination and Result selectors.
- Added Vietnamese and English header auto-detection.
- Added mapping validation and tests.

## Sprint 1B.4 Coverage Completion

- Added branch tests for `HomePage.clear_inspection()` before widget construction.
- Added preview coverage for worksheets without detected headers.
- Added safe sheet-change coverage before workbook inspection exists.
- No production behavior or coverage exclusions were changed.

## 1.2.0-alpha14 — Sprint 1D.1 Revised

- Removed the duplicated Execution Workspace card.
- Placed Column Mapping and Route Provider side by side.
- Connected toolbar Start (F5), Pause/Resume (F6), and Stop (Shift+F5).
- Added an explicit IDLE/RUNNING/PAUSED execution state machine in MainWindow.
- Locked workbook and route configuration while a calculation is active.


## 1.2.0-alpha17 — URL-first Google Maps batch lifecycle

- Opens Google Maps with a complete path-based directions URL for each request.
- Removes origin/destination input filling and Enter-based route submission.
- Keeps one Chromium browser and context alive for the complete batch.
- Creates and closes only one page per route request.
- Waits for the first route card before parsing route information.
- Preserves standalone provider calculation by owning a temporary browser lifecycle.

## 1.2.0-alpha18 — Developer Diagnostics Framework

- Added persistent Debug menu backed by QSettings.
- Added browser navigation and route-card trace logging.
- Added per-route parser diagnostic logging.
- Added optional HTML, full-page screenshot and parser JSON artifacts.
- Added runtime DEBUG/INFO logger switching.

## 1.2.0-alpha20 — Sprint 2.0.1 Read Workbook

- Added streaming Excel and CSV batch readers.
- Added RouteJob models, validation, row mapping, queue construction, and state-aware BatchQueue.
- Reused the batch pipeline from CalculationJobBuilder.

## 1.2.0-alpha27

- Added browser health checks before every Google Maps request.
- Added smart recovery classification for timeout, closed page/context, and
  disconnected browser failures.
- Added safe Playwright cleanup and browser restart support.
- Added browser recovery runtime metrics and diagnostic events.

## 1.2.0-alpha28

- Added provider runtime performance metrics.
- Added adaptive Playwright page reuse and recycling.
- Added proactive recycling for slow and failed requests.
