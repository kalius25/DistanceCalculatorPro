"""Run synthetic 100, 1,000 and 10,000-job batch benchmarks."""

from __future__ import annotations

from app.benchmarks import BatchBenchmarkRunner, BenchmarkReportWriter


def main() -> None:
    runner = BatchBenchmarkRunner()
    results = [
        runner.run(
            job_count,
            lambda _index: None,
            pacing=lambda _index: None,
            autosave=lambda _index: None,
        )
        for job_count in (100, 1_000, 10_000)
    ]
    path = BenchmarkReportWriter().write(results)
    print(path)


if __name__ == "__main__":
    main()
