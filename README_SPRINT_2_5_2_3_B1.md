# Sprint 2.5.2.3-B1 — Gate Runner, Exit Codes & CLI

Adds a deterministic CI performance gate that compares stress benchmark results
with approved baselines.

## CLI

```powershell
python -m app.benchmarks.performance_gate `
  --baseline benchmark-baseline.json `
  --results stress-benchmark.json `
  --output artifacts\performance
```

Use `--fail-on-warning` to return exit code 1 for warning-level comparisons.

## Exit codes

- `0`: PASS or WARNING (unless strict warning mode is enabled)
- `1`: REGRESSION, or WARNING with `--fail-on-warning`
- `2`: invalid or incomplete input

## Outputs

- `performance-gate.json`
- `performance-gate.md`
