from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from app.enums.provider_type import ProviderType
from app.enums.route_preference import RoutePreference
from app.enums.travel_mode import TravelMode
from app.presentation.execution.job import CalculationJob, CalculationJobBuilder
from app.presentation.workspace_configuration import (
    ColumnMapping,
    ProviderConfiguration,
    WorkspaceConfiguration,
)


def make_job(file_path: Path, sheet_name: str = "Routes") -> CalculationJob:
    return CalculationJob(
        str(file_path),
        sheet_name,
        WorkspaceConfiguration(
            ColumnMapping("Origin", "Destination", "Distance"),
            ProviderConfiguration(
                ProviderType.GOOGLE_MAPS_WEB,
                TravelMode.DRIVING,
                avoid_tolls=True,
                avoid_highways=True,
                avoid_ferries=True,
            ),
        ),
    )


def test_build_excel_requests_with_route_options(tmp_path: Path) -> None:
    path = tmp_path / "routes.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Routes"
    sheet.append(["Origin", "Destination", "Distance"])
    sheet.append(["A", "B", None])
    sheet.append([None, None, None])
    sheet.append(["Only origin", None, None])
    sheet.append([" C ", " D ", None])
    workbook.save(path)
    workbook.close()

    requests = CalculationJobBuilder().build_requests(make_job(path))

    assert [(item.origin, item.destination) for item in requests] == [
        ("A", "B"),
        ("C", "D"),
    ]
    request = requests[0]
    assert request.travel_mode is TravelMode.DRIVING
    assert request.toll_preference is RoutePreference.AVOID
    assert request.highway_preference is RoutePreference.AVOID
    assert request.ferry_preference is RoutePreference.AVOID
    assert request.metadata == {
        "row_number": 2,
        "result_column": "Distance",
    }


def test_build_csv_requests_uses_automatic_preferences(tmp_path: Path) -> None:
    path = tmp_path / "routes.csv"
    path.write_text("Origin,Destination,Distance\nA,B,\n", encoding="utf-8")
    job = make_job(path)
    provider = ProviderConfiguration(
        ProviderType.GOOGLE_MAPS_WEB,
        TravelMode.WALKING,
    )
    job = CalculationJob(
        job.file_path,
        job.sheet_name,
        WorkspaceConfiguration(job.configuration.column_mapping, provider),
    )

    request = CalculationJobBuilder().build_requests(job)[0]

    assert request.travel_mode is TravelMode.WALKING
    assert request.toll_preference is RoutePreference.AUTO
    assert request.highway_preference is RoutePreference.AUTO
    assert request.ferry_preference is RoutePreference.AUTO


def test_builder_rejects_missing_unsupported_and_invalid_inputs(
    tmp_path: Path,
) -> None:
    builder = CalculationJobBuilder()
    missing = tmp_path / "missing.xlsx"
    with pytest.raises(FileNotFoundError, match="Workbook not found"):
        builder.build_requests(make_job(missing))

    unsupported = tmp_path / "routes.txt"
    unsupported.touch()
    with pytest.raises(ValueError, match="Unsupported workbook type"):
        builder.build_requests(make_job(unsupported))

    csv_path = tmp_path / "invalid.csv"
    csv_path.write_text("Wrong,Destination\nA,B\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing mapped columns: Origin"):
        builder.build_requests(make_job(csv_path))


def test_builder_handles_missing_sheet_empty_csv_and_short_rows(
    tmp_path: Path,
) -> None:
    builder = CalculationJobBuilder()
    excel_path = tmp_path / "routes.xlsx"
    workbook = Workbook()
    workbook.save(excel_path)
    workbook.close()
    with pytest.raises(ValueError, match="Worksheet not found"):
        builder.build_requests(make_job(excel_path, "Missing"))

    empty_csv = tmp_path / "empty.csv"
    empty_csv.touch()
    with pytest.raises(ValueError, match="Missing mapped columns"):
        builder.build_requests(make_job(empty_csv))

    assert builder._cell(["A"], 3) == ""
    assert builder._cell([None], 0) == ""


def test_build_queue_preserves_all_row_states(tmp_path: Path) -> None:
    path = tmp_path / "routes.csv"
    path.write_text(
        "Origin,Destination,Distance\n"
        "A,B,\n"
        ",B,\n"
        '"10.0,999",invalid,\n'
        "C,C,\n",
        encoding="utf-8",
    )

    queue = CalculationJobBuilder().build_queue(make_job(path))

    assert len(queue) == 4
    assert queue.pending_count == 1
    assert queue.skipped_count == 1
    assert queue.invalid_count == 1
    assert queue.done_count == 1
