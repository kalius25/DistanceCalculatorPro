# Sprint 1D.1 Revised — Toolbar Execution Control

## Delivered

- Execution Card removed from HomePage.
- Column Mapping and Route Provider use one horizontal configuration row.
- Start, Pause/Resume and Stop toolbar actions are state-driven.
- MainWindow emits calculation request, pause, resume and stop signals.
- HomePage remains responsible for rendering and enabling/disabling configuration inputs.

## Execution states

- IDLE: Start enabled only when workspace configuration is valid.
- RUNNING: workspace locked; Pause and Stop enabled.
- PAUSED: workspace stays locked; Pause action becomes Resume.

The calculation worker remains outside this sprint. Controllers can connect to the new MainWindow signals without coupling the view to a concrete calculation service.
