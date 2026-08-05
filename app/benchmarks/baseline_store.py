"""JSON persistence for approved benchmark baselines."""

from __future__ import annotations

import json
from pathlib import Path

from .regression_models import BenchmarkBaseline


class BenchmarkBaselineStore:
    """Load and save versioned benchmark baseline files."""

    SCHEMA_VERSION = 1

    def load(self, path: str | Path) -> tuple[BenchmarkBaseline, ...]:
        source = Path(path)
        if not source.exists():
            return ()
        try:
            payload = json.loads(source.read_text(encoding="utf-8"))
            if payload.get("schema_version") != self.SCHEMA_VERSION:
                raise ValueError("Unsupported benchmark baseline schema version.")
            raw_baselines = payload.get("baselines")
            if not isinstance(raw_baselines, list):
                raise ValueError("Benchmark baseline list is invalid.")
            baselines = tuple(BenchmarkBaseline(**item) for item in raw_baselines)
        except (json.JSONDecodeError, TypeError, AttributeError) as error:
            raise ValueError("Benchmark baseline file is invalid.") from error
        self._ensure_unique(baselines)
        return baselines

    def save(
        self,
        path: str | Path,
        baselines: tuple[BenchmarkBaseline, ...] | list[BenchmarkBaseline],
    ) -> Path:
        target = Path(path)
        normalized = tuple(baselines)
        self._ensure_unique(normalized)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "baselines": [
                baseline.to_dict()
                for baseline in sorted(normalized, key=lambda item: item.scenario)
            ],
        }
        target.write_text(
            json.dumps(payload, indent=2, sort_keys=True),
            encoding="utf-8",
        )
        return target

    def find(
        self,
        baselines: tuple[BenchmarkBaseline, ...] | list[BenchmarkBaseline],
        scenario: str,
    ) -> BenchmarkBaseline:
        for baseline in baselines:
            if baseline.scenario == scenario:
                return baseline
        raise KeyError(f"Benchmark baseline not found: {scenario}")

    @staticmethod
    def _ensure_unique(baselines: tuple[BenchmarkBaseline, ...]) -> None:
        scenarios = [baseline.scenario for baseline in baselines]
        if len(scenarios) != len(set(scenarios)):
            raise ValueError("Duplicate benchmark baseline scenario.")


__all__ = ["BenchmarkBaselineStore"]
