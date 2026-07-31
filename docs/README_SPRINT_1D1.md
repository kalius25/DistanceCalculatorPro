# Sprint 1D.1 — Execution Workspace

Adds a dedicated `ExecutionCard` that summarizes the active workbook job and exposes validated Start/Stop controls. Starting emits the immutable `WorkspaceConfiguration`, locks all configuration controls, and changes the action to Stop. Stopping unlocks configuration and emits a stop request. No calculation worker is started in this sprint.
