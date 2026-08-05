import json
from pathlib import Path

import pytest

from app.benchmarks import BenchmarkBaseline, BenchmarkBaselineStore

pytestmark = pytest.mark.performance_regression


def baseline(name: str) -> BenchmarkBaseline:
    return BenchmarkBaseline(name, 1.0, 2.0, 3.0, 4)


def test_store_saves_loads_sorts_and_finds(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "baseline.json"
    store = BenchmarkBaselineStore()

    assert store.load(path) == ()
    assert store.save(path, [baseline("z"), baseline("a")]) == path

    loaded = store.load(path)
    assert [item.scenario for item in loaded] == ["a", "z"]
    assert store.find(loaded, "z").scenario == "z"

    with pytest.raises(KeyError, match="missing"):
        store.find(loaded, "missing")


def test_store_rejects_duplicate_invalid_and_unsupported_payloads(
    tmp_path: Path,
) -> None:
    store = BenchmarkBaselineStore()
    path = tmp_path / "baseline.json"

    with pytest.raises(ValueError, match="Duplicate"):
        store.save(path, [baseline("x"), baseline("x")])

    payloads = (
        "not json",
        json.dumps({"schema_version": 2, "baselines": []}),
        json.dumps({"schema_version": 1, "baselines": {}}),
        json.dumps({"schema_version": 1, "baselines": [None]}),
    )
    for payload in payloads:
        path.write_text(payload, encoding="utf-8")
        with pytest.raises(ValueError):
            store.load(path)

    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "baselines": [baseline("x").to_dict(), baseline("x").to_dict()],
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="Duplicate"):
        store.load(path)
