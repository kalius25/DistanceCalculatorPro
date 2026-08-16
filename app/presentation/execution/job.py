"""Models and input loading for calculation execution."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.batch.batch_queue import BatchQueue
from app.batch.models import RouteJobStatus
from app.batch.queue_builder import QueueBuilder
from app.exceptions.provider_exception import ProviderException
from app.models.route_request import RouteRequest
from app.presentation.workspace_configuration import WorkspaceConfiguration
from app.providers.catalog import provider_definition


@dataclass(frozen=True, slots=True)
class CalculationJob:
    """A validated workbook calculation job."""

    file_path: str
    sheet_name: str
    configuration: WorkspaceConfiguration
    output_path: str | None = None


Row = Sequence[object]


class CalculationJobBuilder:
    """Build route requests from the reusable batch queue pipeline."""

    def __init__(self, queue_builder: QueueBuilder | None = None) -> None:
        self._queue_builder = queue_builder or QueueBuilder()

    def build_queue(self, job: CalculationJob) -> BatchQueue:
        """Build the reusable state-aware queue for one calculation job."""
        selected_provider = (
            job.configuration.provider_configuration.provider
        )
        definition = provider_definition(selected_provider)
        if not definition.execution_enabled:
            raise ProviderException(
                f"{definition.display_name} is not executable yet; "
                f"planned for Sprint {definition.roadmap_sprint}."
            )

        return self._queue_builder.build(
            job.file_path,
            job.sheet_name,
            job.configuration,
        )

    def build_requests(self, job: CalculationJob) -> list[RouteRequest]:
        queue = self.build_queue(job)
        return [
            RouteRequest(
                origin=item.origin,
                destination=item.destination,
                travel_mode=item.travel_mode,
                toll_preference=item.toll_preference,
                ferry_preference=item.ferry_preference,
                highway_preference=item.highway_preference,
                metadata={
                    **item.metadata,
                    "row_number": item.row_index,
                    "result_column": item.result_column,
                },
            )
            for item in queue
            if item.status is RouteJobStatus.PENDING
        ]

    @staticmethod
    def _cell(row: Row, index: int) -> str:
        """Compatibility helper retained for existing execution tests."""
        if index >= len(row):
            return ""
        value = row[index]
        return "" if value is None else str(value).strip()
