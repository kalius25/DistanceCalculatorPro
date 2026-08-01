"""Core models for workbook-backed batch route processing."""

from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import Enum

from app.enums.route_preference import RoutePreference
from app.enums.travel_mode import TravelMode


class RouteJobStatus(Enum):
    """Lifecycle state of one workbook route job."""

    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"
    SKIPPED = "skipped"
    RETRY = "retry"
    INVALID = "invalid"


@dataclass(slots=True)
class RouteJob:
    """One normalized workbook row ready for batch processing."""

    row_index: int
    origin: str
    destination: str
    result_column: str
    travel_mode: TravelMode = TravelMode.DRIVING
    toll_preference: RoutePreference = RoutePreference.AUTO
    ferry_preference: RoutePreference = RoutePreference.AUTO
    highway_preference: RoutePreference = RoutePreference.AUTO
    status: RouteJobStatus = RouteJobStatus.PENDING
    retry_count: int = 0
    validation_error: str | None = None
    result_distance_km: float | None = None
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class WorkbookRow:
    """A worksheet row with its original one-based row number."""

    row_number: int
    values: tuple[object, ...]


@dataclass(frozen=True, slots=True)
class WorkbookStream:
    """Streaming worksheet content and normalized headers."""

    headers: tuple[str, ...]
    rows: Iterator[WorkbookRow]
