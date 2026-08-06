import json
from pathlib import Path

import pytest

from app.benchmarks import (
    BaselineUpdateInputError,
    BaselineUpdateMode,
    BaselineUpdateReportWriter,
    BaselineUpdateRunner,
    BenchmarkBaselineStore,
)

pytestmark = pytest.mark.baseline_management


def write_results(path: Path, *items: tuple[str, float]) -> None:
    path.write_text(
        json.dumps(
            {
                "results": [
                    {
                        "scenario": name,
                        "rows": 100,
                        "iterations": 1,
                        "elapsed_seconds": elapsed,
                        "rows_per_second": 100 / elapsed,
                        "peak_memory_bytes": 1_048_576,
                        "autosave_count": 1,
                        "average_row_latency_seconds": 0.01,
                        "maximum_row_latency_seconds": 0.02,
                    }
                    for name, elapsed in items
                ]
            }
        ),
        encoding="utf-8",
    )


def test_create_merge_replace_filter_and_dry_run(tmp_path: Path) -> None:
    results = tmp_path / "results.json"
    output = tmp_path / "baseline.json"
    write_results(results, ("smoke", 1.0), ("1k", 2.0))
    runner = BaselineUpdateRunner()

    created = runner.run(results, output)
    assert created.mode is BaselineUpdateMode.CREATE
    assert created.added == ("1k", "smoke")
    assert created.changed

    with pytest.raises(BaselineUpdateInputError, match="already exists"):
        runner.run(results, output)

    write_results(results, ("smoke", 1.5), ("5k", 3.0))
    merged = runner.run(results, output, mode=BaselineUpdateMode.MERGE)
    assert merged.added == ("5k",)
    assert merged.updated == ("smoke",)
    assert merged.retained == ("1k",)
    assert merged.removed == ()

    preview = runner.run(
        results,
        output,
        mode=BaselineUpdateMode.REPLACE,
        scenarios=("5k",),
        dry_run=True,
    )
    assert preview.removed == ("1k", "smoke")
    assert BenchmarkBaselineStore().find(BenchmarkBaselineStore().load(output), "smoke")

    replaced = runner.run(
        results,
        output,
        mode=BaselineUpdateMode.REPLACE,
        scenarios=("5k",),
    )
    assert replaced.retained == ("5k",)
    assert [item.scenario for item in BenchmarkBaselineStore().load(output)] == ["5k"]

    with pytest.raises(BaselineUpdateInputError, match="not found"):
        runner.run(results, output, scenarios=("missing",), dry_run=True)


def test_update_report_and_model_serialization(tmp_path: Path) -> None:
    results = tmp_path / "results.json"
    baseline = tmp_path / "baseline.json"
    write_results(results, ("smoke", 1.0))
    result = BaselineUpdateRunner().run(results, baseline)
    json_path, markdown_path = BaselineUpdateReportWriter().write(result, tmp_path)

    assert result.to_dict()["output_path"] == str(baseline)
    assert json.loads(json_path.read_text(encoding="utf-8"))["mode"] == "create"
    assert "Added: smoke" in markdown_path.read_text(encoding="utf-8")


def test_runner_wraps_invalid_input(tmp_path: Path) -> None:
    with pytest.raises(BaselineUpdateInputError):
        BaselineUpdateRunner().run(tmp_path / "missing.json", tmp_path / "x.json")


def test_missing_scenario_message_lists_requested_and_available(
    tmp_path: Path,
) -> None:
    results = tmp_path / "results.json"
    output = tmp_path / "baseline.json"
    write_results(results, ("custom-25000", 1.0))

    with pytest.raises(BaselineUpdateInputError) as raised:
        BaselineUpdateRunner().run(
            results,
            output,
            scenarios=("smoke", "custom-25000"),
            dry_run=True,
        )

    message = str(raised.value)
    assert "Requested benchmark scenario(s) were not found" in message
    assert "  - smoke" in message
    assert "Available scenarios" in message
    assert "  - custom-25000" in message


def test_runner_can_ignore_missing_scenarios_when_one_is_available(
    tmp_path: Path,
) -> None:
    results = tmp_path / "results.json"
    output = tmp_path / "baseline.json"
    write_results(results, ("custom-25000", 1.0))

    result = BaselineUpdateRunner().run(
        results,
        output,
        scenarios=("smoke", "custom-25000", "smoke"),
        ignore_missing_scenarios=True,
    )

    assert result.requested_scenarios == ("smoke", "custom-25000")
    assert result.selected_scenarios == ("custom-25000",)
    assert result.missing_scenarios == ("smoke",)
    assert result.ignored_missing_scenarios
    assert [item.scenario for item in BenchmarkBaselineStore().load(output)] == [
        "custom-25000"
    ]


def test_runner_rejects_when_all_ignored_scenarios_are_missing(
    tmp_path: Path,
) -> None:
    results = tmp_path / "results.json"
    output = tmp_path / "baseline.json"
    write_results(results, ("custom-25000", 1.0))

    with pytest.raises(
        BaselineUpdateInputError,
        match="No requested benchmark scenarios were found",
    ):
        BaselineUpdateRunner().run(
            results,
            output,
            scenarios=("smoke", "10k"),
            ignore_missing_scenarios=True,
            dry_run=True,
        )


def test_update_report_includes_scenario_selection_details(
    tmp_path: Path,
) -> None:
    results = tmp_path / "results.json"
    baseline = tmp_path / "baseline.json"
    write_results(results, ("smoke", 1.0))
    result = BaselineUpdateRunner().run(
        results,
        baseline,
        scenarios=("smoke", "missing"),
        ignore_missing_scenarios=True,
    )

    json_path, markdown_path = BaselineUpdateReportWriter().write(
        result,
        tmp_path / "reports",
    )
    payload = json.loads(json_path.read_text(encoding="utf-8"))
    markdown = markdown_path.read_text(encoding="utf-8")

    assert payload["requested_scenarios"] == ["smoke", "missing"]
    assert payload["selected_scenarios"] == ["smoke"]
    assert payload["missing_scenarios"] == ["missing"]
    assert payload["ignored_missing_scenarios"] is True
    assert "Missing scenarios: missing" in markdown
    assert "Ignored missing scenarios: True" in markdown
