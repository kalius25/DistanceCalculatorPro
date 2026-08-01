import pytest

from app.batch import BatchWorkbookError, RouteJobStatus, RowMapper, WorkbookRow
from app.enums.provider_type import ProviderType
from app.enums.route_preference import RoutePreference
from app.enums.travel_mode import TravelMode
from app.presentation.workspace_configuration import (
    ColumnMapping,
    ProviderConfiguration,
    WorkspaceConfiguration,
)


def configuration() -> WorkspaceConfiguration:
    return WorkspaceConfiguration(
        ColumnMapping("Origin", "Destination", "Distance"),
        ProviderConfiguration(
            ProviderType.GOOGLE_MAPS_WEB,
            TravelMode.DRIVING,
            avoid_tolls=True,
            avoid_highways=True,
            avoid_ferries=True,
        ),
    )


def test_mapper_resolves_indexes_and_maps_route_options() -> None:
    mapper = RowMapper()
    config = configuration()
    indexes = mapper.resolve_indexes(
        ("Origin", "Destination", "Distance"),
        config,
    )

    job = mapper.map_row(
        WorkbookRow(7, (" A ", " B ", None)),
        indexes,
        config,
    )

    assert (job.row_index, job.origin, job.destination) == (7, "A", "B")
    assert job.result_column == "Distance"
    assert job.status is RouteJobStatus.PENDING
    assert job.travel_mode is TravelMode.DRIVING
    assert job.toll_preference is RoutePreference.AVOID
    assert job.highway_preference is RoutePreference.AVOID
    assert job.ferry_preference is RoutePreference.AVOID
    assert job.metadata == {"source_row": 7}


def test_mapper_handles_short_rows_and_validation_outcome() -> None:
    mapper = RowMapper()
    config = configuration()
    indexes = mapper.resolve_indexes(
        ("Origin", "Destination", "Distance"),
        config,
    )

    job = mapper.map_row(WorkbookRow(2, ("A",)), indexes, config)

    assert job.status is RouteJobStatus.SKIPPED
    assert job.destination == ""
    assert job.validation_error is not None


def test_mapper_rejects_missing_mapped_columns() -> None:
    with pytest.raises(
        BatchWorkbookError,
        match="Missing mapped columns: Destination, Distance",
    ):
        RowMapper().resolve_indexes(("Origin",), configuration())
