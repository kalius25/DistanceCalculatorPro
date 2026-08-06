"""Create, merge, or replace approved benchmark baselines."""

from __future__ import annotations

from pathlib import Path

from .baseline_store import BenchmarkBaselineStore
from .baseline_update_models import BaselineUpdateMode, BaselineUpdateResult
from .gate_runner import PerformanceGateInputError, PerformanceGateRunner
from .regression_models import BenchmarkBaseline
from .stress_models import StressBenchmarkResult


class BaselineUpdateInputError(ValueError):
    """Raised when baseline update inputs are invalid."""


class BaselineUpdateRunner:
    """Convert stress benchmark results into approved baselines."""

    def __init__(self, store: BenchmarkBaselineStore | None = None) -> None:
        self._store = store or BenchmarkBaselineStore()

    def run(
        self,
        results_path: str | Path,
        output_path: str | Path,
        *,
        mode: BaselineUpdateMode = BaselineUpdateMode.CREATE,
        scenarios: tuple[str, ...] = (),
        dry_run: bool = False,
        ignore_missing_scenarios: bool = False,
    ) -> BaselineUpdateResult:
        target = Path(output_path)
        requested = tuple(dict.fromkeys(scenarios))
        try:
            results = PerformanceGateRunner._load_results(results_path)
            selected, missing = self._select(
                results,
                requested,
                ignore_missing_scenarios=ignore_missing_scenarios,
            )
            incoming = {
                item.scenario: BenchmarkBaseline.from_result(item) for item in selected
            }
            existing = self._store.load(target)
        except (PerformanceGateInputError, OSError, ValueError, TypeError) as error:
            raise BaselineUpdateInputError(str(error)) from error

        if mode is BaselineUpdateMode.CREATE and existing:
            raise BaselineUpdateInputError(
                "Benchmark baseline already exists; use --merge or --replace."
            )

        old = {item.scenario: item for item in existing}
        if mode is BaselineUpdateMode.MERGE:
            final = {**old, **incoming}
        else:
            final = dict(incoming)

        added = tuple(sorted(set(incoming) - set(old)))
        updated = tuple(
            sorted(
                name for name in set(incoming) & set(old) if incoming[name] != old[name]
            )
        )
        retained = tuple(sorted(set(final) & set(old) - set(updated)))
        removed = tuple(sorted(set(old) - set(final)))

        if not dry_run:
            self._store.save(target, tuple(final.values()))

        return BaselineUpdateResult(
            mode=mode,
            output_path=target,
            dry_run=dry_run,
            added=added,
            updated=updated,
            retained=retained,
            removed=removed,
            requested_scenarios=requested,
            selected_scenarios=tuple(item.scenario for item in selected),
            missing_scenarios=missing,
            ignored_missing_scenarios=bool(missing and ignore_missing_scenarios),
        )

    @staticmethod
    def _select(
        results: tuple[StressBenchmarkResult, ...],
        scenarios: tuple[str, ...],
        *,
        ignore_missing_scenarios: bool,
    ) -> tuple[tuple[StressBenchmarkResult, ...], tuple[str, ...]]:
        if not scenarios:
            return results, ()

        requested = set(scenarios)
        selected = tuple(item for item in results if item.scenario in requested)
        found = {item.scenario for item in selected}
        missing = tuple(sorted(requested - found))
        if missing and not ignore_missing_scenarios:
            available = tuple(sorted(item.scenario for item in results))
            raise BaselineUpdateInputError(
                BaselineUpdateRunner._missing_scenario_message(missing, available)
            )
        if not selected:
            available = tuple(sorted(item.scenario for item in results))
            raise BaselineUpdateInputError(
                "No requested benchmark scenarios were found.\n\n"
                + BaselineUpdateRunner._missing_scenario_message(missing, available)
            )
        return selected, missing

    @staticmethod
    def _missing_scenario_message(
        missing: tuple[str, ...],
        available: tuple[str, ...],
    ) -> str:
        missing_lines = "\n".join(f"  - {name}" for name in missing)
        available_lines = (
            "\n".join(f"  - {name}" for name in available) if available else "  - None"
        )
        return (
            "Requested benchmark scenario(s) were not found:\n\n"
            f"{missing_lines}\n\n"
            "Available scenarios:\n\n"
            f"{available_lines}"
        )


__all__ = ["BaselineUpdateInputError", "BaselineUpdateRunner"]
