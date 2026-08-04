# Sprint 2.5.2.1 — Large Batch Benchmark

This sprint adds deterministic, provider-free stress benchmarks for large route workloads.

## Components

- `RouteWorkloadGenerator`: creates repeatable route requests without workbook or network I/O.
- `StressBenchmarkRunner`: measures elapsed time, throughput, row latency, autosaves, and peak traced memory.
- `StressBenchmarkReportWriter`: exports JSON and Markdown reports.
- `BenchmarkScenario` and `StressBenchmarkResult`: immutable benchmark models.

## Suggested scenarios

- 1,000 rows
- 5,000 rows
- 10,000 rows
- 25,000 rows
- 50,000 rows

## Run tests

```powershell
pytest tests\benchmarks -m benchmark -vv
```

The benchmark modules do not open Qt, Playwright, Chromium, or Google Maps.
