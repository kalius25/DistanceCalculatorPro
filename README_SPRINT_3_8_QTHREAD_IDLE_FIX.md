# Sprint 3.8 — Multi-provider QThread idle fix

The GUI regression harness previously advanced to the next case as soon as
`calculation_completed` was emitted.

That signal is emitted before `CalculationWorker.finished`, `QThread.finished`
and `CalculationExecutionCoordinator._clear_worker()`. Therefore the next
Start could race with the previous thread cleanup and be rejected because the
coordinator was still running.

The regression harness now:

1. verifies the coordinator is idle before each case;
2. triggers Start and verifies a worker actually started;
3. waits for calculation completion/failure;
4. waits for `coordinator.is_running == False`;
5. only then reads results and advances to the next provider/mode.

The report now includes:

```text
Worker idle: True
```

for every passing case.

No production engine/provider/browser code changed.
