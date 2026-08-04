"""Deterministic synthetic workloads for performance benchmarks."""

from __future__ import annotations

from collections.abc import Iterator

from app.models.route_request import RouteRequest


class RouteWorkloadGenerator:
    """Generate repeatable route requests without workbook or network I/O."""

    def generate(self, rows: int) -> Iterator[RouteRequest]:
        if rows < 1:
            raise ValueError("Workload rows must be positive.")
        for index in range(rows):
            yield RouteRequest(
                origin=f"Origin {index}",
                destination=f"Destination {index}",
            )


__all__ = ["RouteWorkloadGenerator"]
