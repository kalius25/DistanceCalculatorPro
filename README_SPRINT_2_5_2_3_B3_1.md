# Sprint 2.5.2.3-B3.1 — Baseline Creation & Merge CLI

Create a new approved baseline:

```powershell
python -m app.benchmarks.create_baseline `
  --results artifacts\benchmarks\stress-benchmark.json `
  --output benchmark-baseline.json
```

Merge current results into an existing baseline:

```powershell
python -m app.benchmarks.create_baseline `
  --results artifacts\benchmarks\stress-benchmark.json `
  --output benchmark-baseline.json `
  --merge
```

Replace the existing baseline, select specific scenarios, or preview changes with
`--replace`, repeated `--scenario`, and `--dry-run`.

Each run creates `baseline-update.json` and `baseline-update.md`. Use
`--report-output` to choose their directory.
