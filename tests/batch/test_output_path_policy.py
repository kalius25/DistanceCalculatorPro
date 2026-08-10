from pathlib import Path

from app.batch.output_path_policy import OutputPathPolicy


def test_output_path_policy_builds_safe_sibling_path() -> None:
    source = Path("reports/routes.xlsm")

    assert OutputPathPolicy().build(source) == Path("reports/routes.result.xlsm")


def test_output_path_policy_always_creates_a_distinct_result_path() -> None:
    source = Path("reports/routes.result.xlsx")
    assert OutputPathPolicy().build(source) == Path("reports/routes.result.result.xlsx")
