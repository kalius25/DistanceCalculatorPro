import pytest
from unittest.mock import MagicMock

from app.controllers.calculation_controller import (
    CalculationController,
    ColumnMapping,
)
from app.models.route_request import RouteRequest


def make_mapping(
    origin="Origin",
    destination="Destination",
    distance="Distance",
    duration="Duration",
):
    return ColumnMapping(
        origin=origin,
        destination=destination,
        distance=distance,
        duration=duration,
    )


def test_constructor():
    excel = MagicMock()

    controller = CalculationController(excel)

    assert controller._excel is excel


def test_get_sheet_names():
    excel = MagicMock()
    excel.get_sheet_names.return_value = ["Sheet1", "Sheet2"]

    controller = CalculationController(excel)

    assert controller.get_sheet_names() == ["Sheet1", "Sheet2"]

    excel.get_sheet_names.assert_called_once()


def test_get_headers():
    excel = MagicMock()
    excel.read_headers.return_value = ["A", "B"]

    controller = CalculationController(excel)

    assert controller.get_headers("Data") == ["A", "B"]

    excel.read_headers.assert_called_once_with("Data")


def test_get_preview():
    excel = MagicMock()

    excel.read_headers.return_value = ["A", "B"]

    excel.read_preview.return_value = [
        ["1", "2"],
        ["3", "4"],
    ]

    controller = CalculationController(excel)

    headers, rows = controller.get_preview(
        "Sheet1",
        max_rows=5,
    )

    assert headers == ["A", "B"]

    assert rows == [
        ["1", "2"],
        ["3", "4"],
    ]

    excel.read_headers.assert_called_once_with("Sheet1")

    excel.read_preview.assert_called_once_with(
        "Sheet1",
        max_rows=5,
    )


@pytest.mark.parametrize(
    "mapping, expected",
    [
        (
            make_mapping(origin=""),
            (False, "Chưa chọn Origin."),
        ),
        (
            make_mapping(destination=""),
            (False, "Chưa chọn Destination."),
        ),
        (
            make_mapping(
                origin="A",
                destination="A",
            ),
            (
                False,
                "Origin và Destination không được trùng.",
            ),
        ),
        (
            make_mapping(distance=""),
            (
                False,
                "Chưa chọn cột Distance.",
            ),
        ),
        (
            make_mapping(duration=""),
            (
                False,
                "Chưa chọn cột Duration.",
            ),
        ),
        (
            make_mapping(),
            (
                True,
                "",
            ),
        ),
    ],
)
def test_validate_mapping(mapping, expected):
    controller = CalculationController(MagicMock())

    assert controller.validate_mapping(mapping) == expected


def test_build_requests_invalid_mapping():
    controller = CalculationController(MagicMock())

    with pytest.raises(ValueError, match="Chưa chọn Origin."):
        controller.build_requests(
            "Sheet1",
            make_mapping(origin=""),
        )


def test_build_requests():
    excel = MagicMock()

    excel.read_headers.return_value = [
        "Origin",
        "Destination",
        "Distance",
        "Duration",
    ]

    excel.read_all.return_value = [
        [
            "  Ha Noi  ",
            "  Hai Phong ",
            100,
            120,
        ],
        [
            "Can Tho",
            "Ca Mau",
            180,
            200,
        ],
    ]

    controller = CalculationController(excel)

    requests = controller.build_requests(
        "Sheet1",
        make_mapping(),
    )

    assert len(requests) == 2

    assert isinstance(
        requests[0],
        RouteRequest,
    )

    assert requests[0].origin == "Ha Noi"
    assert requests[0].destination == "Hai Phong"
    assert requests[0].metadata["row_number"] == 2

    assert requests[1].origin == "Can Tho"
    assert requests[1].destination == "Ca Mau"
    assert requests[1].metadata["row_number"] == 3

    excel.read_headers.assert_called_once_with("Sheet1")
    excel.read_all.assert_called_once_with("Sheet1")