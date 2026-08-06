# Sprint 2.5.2.3-B3.2 — Baseline CLI UX & GitHub Actions

## Baseline CLI

Strict mode reports every requested scenario that is missing and lists all
available scenarios from the benchmark result file.

Use lenient selection when a result file intentionally contains only part of
the approved scenario set:

```powershell
python -m app.benchmarks.create_baseline `
  --results artifacts\benchmarks\stress-benchmark.json `
  --output benchmark-baseline.json `
  --merge `
  --scenario smoke `
  --scenario custom-25000 `
  --ignore-missing-scenarios
```

At least one requested scenario must still exist. The JSON and Markdown update
reports record requested, selected, missing, and ignored scenarios.

## CI workflow

`.github/workflows/performance-regression.yml` runs a smoke benchmark for pull
requests and supports full benchmark runs on a schedule or by manual dispatch.
Benchmark and performance-gate reports are always uploaded as workflow
artifacts.
