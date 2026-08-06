from pathlib import Path

import pytest

pytestmark = pytest.mark.baseline_management


def test_performance_regression_workflow_contains_required_steps() -> None:
    workflow = Path(".github/workflows/performance-regression.yml").read_text(
        encoding="utf-8"
    )

    assert "pull_request:" in workflow
    assert "workflow_dispatch:" in workflow
    assert "schedule:" in workflow
    assert "python -m app.benchmarks.run_stress" in workflow
    assert "python -m app.benchmarks.performance_gate" in workflow
    assert "actions/upload-artifact@v4" in workflow
    assert "stress-benchmark.json" in workflow
    assert "performance-gate.json" in workflow
    assert "benchmark-baseline.json" in workflow
