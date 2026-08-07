# Sprint 2.6.2 UI Flow Revision

This revision aligns the workspace with the requested file-selection and workbook-inspection flow.

## Startup

- Shows only Drag & Drop and Recent Workbooks.
- Removes File Information from the visible workspace.
- Drag & Drop receives roughly one third of the vertical space.
- Recent Workbooks receives roughly two thirds.
- Workbook Inspector is hidden until a workbook has been inspected.
- The File Panels toggle reads `Hide File Panels` and is enabled once a workbook is available.

## Workbook loaded

- Drag & Drop and Recent Workbooks are hidden automatically.
- Workbook Inspector becomes the primary workspace.
- The File Panels toggle reads `Show File Panels`.
- Toggling back shows the two file-selection panels and hides Workbook Inspector.

## Workbook Inspector metadata

- `File Path` and `File Size` are displayed directly below the Workbook Inspector heading.
- Worksheet, Preview rows, Rows, Columns, and Detected headers remain below the file metadata.

## Configuration focus

- Added `Hide Config` / `Show Config` beside the Workbook Inspector heading.
- Hiding configuration collapses Column Mapping and Route Provider.
- Data Preview automatically receives the released vertical space.

## Compatibility hardening

- Splitter state restore now ignores unsupported values instead of passing them to Qt.
- Startup always begins in the file-selection workspace regardless of the previous file-panel preference.
