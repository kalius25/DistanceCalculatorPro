"""Map streaming workbook rows into normalized route jobs."""

from __future__ import annotations

from app.enums.route_preference import RoutePreference
from app.presentation.workspace_configuration import WorkspaceConfiguration

from .exceptions import BatchWorkbookError
from .models import RouteJob, WorkbookRow
from .resume_analyzer import ResumeAnalyzer
from .row_validator import RowValidator


class RowMapper:
    """Convert one workbook row using the selected workspace mapping."""

    def __init__(
        self,
        validator: RowValidator | None = None,
        resume_analyzer: ResumeAnalyzer | None = None,
    ) -> None:
        self._validator = validator or RowValidator()
        self._resume_analyzer = resume_analyzer or ResumeAnalyzer()

    def resolve_indexes(
        self,
        headers: tuple[str, ...],
        configuration: WorkspaceConfiguration,
    ) -> dict[str, int]:
        indexes = {header: index for index, header in enumerate(headers)}
        mapping = configuration.column_mapping
        required = (
            mapping.origin_column,
            mapping.destination_column,
            mapping.result_column,
            *(
                [mapping.result_duration_column]
                if mapping.result_duration_column
                else []
            ),
        )
        missing = [column for column in required if column not in indexes]
        if missing:
            raise BatchWorkbookError("Missing mapped columns: " + ", ".join(missing))
        return indexes

    def map_row(
        self,
        row: WorkbookRow,
        indexes: dict[str, int],
        configuration: WorkspaceConfiguration,
    ) -> RouteJob:
        mapping = configuration.column_mapping
        provider = configuration.provider_configuration
        origin = self._cell(row.values, indexes[mapping.origin_column])
        destination = self._cell(
            row.values,
            indexes[mapping.destination_column],
        )
        validation = self._validator.validate(origin, destination)
        result_value = self._raw_cell(row.values, indexes[mapping.result_column])
        resume = self._resume_analyzer.analyze(
            result_value, configuration.skip_existing_results
        )
        status = validation.status
        distance_km = validation.distance_km
        metadata: dict[str, object] = {
            "source_row": row.row_number,
            "provider": provider.provider,
        }
        if status.value == "pending" and resume.should_skip:
            status = resume.status
            distance_km = resume.distance_km
            metadata["resumed_existing_result"] = True
            metadata["existing_result"] = result_value
        avoid = RoutePreference.AVOID
        automatic = RoutePreference.AUTO
        return RouteJob(
            row_index=row.row_number,
            origin=origin,
            destination=destination,
            result_column=mapping.result_column,
            result_duration_column=mapping.result_duration_column,
            travel_mode=provider.travel_mode,
            toll_preference=avoid if provider.avoid_tolls else automatic,
            highway_preference=(avoid if provider.avoid_highways else automatic),
            ferry_preference=(avoid if provider.avoid_ferries else automatic),
            status=status,
            validation_error=validation.message,
            result_distance_km=distance_km,
            metadata=metadata,
        )

    @staticmethod
    def _raw_cell(values: tuple[object, ...], index: int) -> object:
        if index >= len(values):
            return None
        return values[index]

    @staticmethod
    def _cell(values: tuple[object, ...], index: int) -> str:
        if index >= len(values):
            return ""
        value = values[index]
        return "" if value is None else str(value).strip()
