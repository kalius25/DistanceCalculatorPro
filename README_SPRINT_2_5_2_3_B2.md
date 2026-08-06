# Sprint 2.5.2.3-B2 — Benchmark CLI & CI Artifact Flow

Run the deterministic stress benchmark without GUI, browser, or network:

```powershell
python -m app.benchmarks.run_stress `
  --output artifacts\benchmarks
```

This creates stable CI artifacts:

- `artifacts/benchmarks/stress-benchmark.json`
- `artifacts/benchmarks/stress-benchmark.md`

Run all predefined scenarios:

```powershell
python -m app.benchmarks.run_stress `
  --all `
  --output artifacts\benchmarks
```

Run a custom workload:

```powershell
python -m app.benchmarks.run_stress `
  --rows 25000 `
  --iterations 2 `
  --autosave-interval 100 `
  --output artifacts\benchmarks
```

Then execute the performance gate:

```powershell
python -m app.benchmarks.performance_gate `
  --baseline benchmark-baseline.json `
  --results artifacts\benchmarks\stress-benchmark.json `
  --output artifacts\performance
```
