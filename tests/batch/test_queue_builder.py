from pathlib import Path

from openpyxl import Workbook

from app.batch import QueueBuilder, RouteJobStatus
from app.enums.provider_type import ProviderType
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
        ),
    )


def test_queue_builder_creates_jobs_for_all_source_rows(tmp_path: Path) -> None:
    path = tmp_path / "routes.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Routes"
    sheet.append(["Origin", "Destination", "Distance"])
    sheet.append(["A", "B", None])
    sheet.append(["", "B", None])
    sheet.append(["C", "C", None])
    sheet.append(["91,106", "10,106", None])
    workbook.save(path)

    queue = QueueBuilder().build(path, "Routes", configuration())

    assert len(queue) == 4
    assert queue.ready_count == 1
    assert queue.skipped_count == 1
    assert queue.invalid_count == 1
    assert queue.count(RouteJobStatus.DONE) == 1
