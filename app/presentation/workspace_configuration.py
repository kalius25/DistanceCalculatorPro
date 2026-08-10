"""Immutable presentation models for a distance-calculation workspace."""

from dataclasses import dataclass

from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode


@dataclass(frozen=True, slots=True)
class ColumnMapping:
    """Selected workbook columns used by a calculation job."""

    origin_column: str
    destination_column: str
    result_column: str
    result_duration_column: str = ""


@dataclass(frozen=True, slots=True)
class ProviderConfiguration:
    """Selected route provider and route options."""

    provider: ProviderType
    travel_mode: TravelMode
    avoid_tolls: bool = False
    avoid_highways: bool = False
    avoid_ferries: bool = False


@dataclass(frozen=True, slots=True)
class WorkspaceConfiguration:
    """Complete validated configuration required to start a job."""

    column_mapping: ColumnMapping
    provider_configuration: ProviderConfiguration
    skip_existing_results: bool = True
