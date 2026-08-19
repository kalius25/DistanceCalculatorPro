from unittest.mock import MagicMock, patch

import pytest

from app.parsers.vietbando_parser import (
    VietBanDoParser,
    _extract_distance_text,
)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("Tổng chiều dài: 128.1 km", "128.1 km"),
        ("Chiều dài: 128.441km", "128.441 km"),
        ("Tổng chiều dài: 950 m", "950 m"),
        ("Không có kết quả", None),
    ],
)
def test_extract_distance_text(
    text: str,
    expected: str | None,
) -> None:
    assert _extract_distance_text(text) == expected


def test_parse_reads_live_vietbando_total_distance() -> None:
    page = MagicMock()
    distance = MagicMock()
    distance.inner_text.return_value = "Tổng chiều dài: 128.1 km"

    with patch(
        "app.parsers.vietbando_parser." "VietBanDoLocator.route_distance",
        return_value=distance,
    ):
        routes = VietBanDoParser.parse(page)

    assert len(routes) == 1
    route = routes[0]
    assert route.summary == "Tổng chiều dài: 128.1 km"
    assert route.distance_text == "128.1 km"
    assert route.distance_km == 128.1
    assert route.duration_text == ""
    assert route.duration_minutes == 0
    assert route.raw == {
        "provider": "vietbando_web",
        "summary_text": "Tổng chiều dài: 128.1 km",
        "distance_text": "128.1 km",
        "duration_available": False,
    }


def test_parse_supports_truck_precision() -> None:
    page = MagicMock()
    distance = MagicMock()
    distance.inner_text.return_value = "Tổng chiều dài: 128.441 km"

    with patch(
        "app.parsers.vietbando_parser." "VietBanDoLocator.route_distance",
        return_value=distance,
    ):
        routes = VietBanDoParser.parse(page)

    assert routes[0].distance_km == 128.441


def test_parse_logs_route_when_diagnostics_present() -> None:
    page = MagicMock()
    diagnostics = MagicMock()
    distance = MagicMock()
    distance.inner_text.return_value = "Tổng chiều dài: 126.774 km"

    with patch(
        "app.parsers.vietbando_parser." "VietBanDoLocator.route_distance",
        return_value=distance,
    ):
        routes = VietBanDoParser.parse(page, diagnostics)

    diagnostics.log_routes.assert_called_once()
    assert routes[0].distance_km == 126.774


def test_parse_returns_empty_when_summary_has_no_metric() -> None:
    page = MagicMock()
    distance = MagicMock()
    distance.inner_text.return_value = "Đang tìm đường"

    with patch(
        "app.parsers.vietbando_parser." "VietBanDoLocator.route_distance",
        return_value=distance,
    ):
        assert VietBanDoParser.parse(page) == []


def test_parse_returns_empty_when_converter_rejects_metric() -> None:
    page = MagicMock()
    distance = MagicMock()
    distance.inner_text.return_value = "Tổng chiều dài: 128.1 km"

    with (
        patch(
            "app.parsers.vietbando_parser." "VietBanDoLocator.route_distance",
            return_value=distance,
        ),
        patch(
            "app.parsers.vietbando_parser." "TextConverter.distance_to_km",
            return_value=None,
        ),
    ):
        assert VietBanDoParser.parse(page) == []
