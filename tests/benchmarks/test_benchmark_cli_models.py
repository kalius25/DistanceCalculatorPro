from pathlib import Path

import pytest

from app.benchmarks import BenchmarkCliExitCode, BenchmarkCliResult

pytestmark = [pytest.mark.benchmark, pytest.mark.benchmark_cli]


def test_benchmark_cli_models_store_results_and_exit_codes() -> None:
    result = BenchmarkCliResult((), Path("result.json"), Path("result.md"))

    assert result.results == ()
    assert result.json_path == Path("result.json")
    assert int(BenchmarkCliExitCode.SUCCESS) == 0
    assert int(BenchmarkCliExitCode.INVALID_INPUT) == 2
    assert int(BenchmarkCliExitCode.RUNTIME_ERROR) == 3
