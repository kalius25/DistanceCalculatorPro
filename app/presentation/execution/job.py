"""Models and input loading for calculation execution."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from app.batch.models import RouteJobStatus
from app.batch.queue_builder import QueueBuilder
from app.models.route_request import RouteRequest
from app.presentation.workspace_configuration import WorkspaceConfiguration


@dataclass(frozen=True, slots=True)
class CalculationJob:
    """A validated workbook calculation job."""

    file_path: str
    sheet_name: str
    configuration: WorkspaceConfiguration


Row = Sequence[object]


class CalculationJobBuilder:
    """Build route requests from the reusable batch queue pipeline."""

    def __init__(self, queue_builder: QueueBuilder | None = None) -> None:
        self._queue_builder = queue_builder or QueueBuilder()

    def build_requests(self, job: CalculationJob) -> list[RouteRequest]:
        queue = self._queue_builder.build(
            job.file_path,
            job.sheet_name,
            job.configuration,
        )
        return [
            RouteRequest(
                origin=item.origin,
                destination=item.destination,
                travel_mode=item.travel_mode,
                toll_preference=item.toll_preference,
                ferry_preference=item.ferry_preference,
                highway_preference=item.highway_preference,
                metadata={
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
