from unittest.mock import patch

from app.parsers.route_text_parser import parse_route_text
from app.utils.text_converter import TextConverter


def test_parse_route_text_extracts_metrics_and_flags() -> None:
    option = parse_route_text(
        "QL1A\n1.5 km\n1 giờ 20 phút\nToll highway ferry",
        provider="sample",
    )

    assert option is not None
    assert option.summary == "QL1A"
    assert option.distance_km == 1.5
    assert option.duration_minutes == 80
    assert option.has_toll
    assert option.has_highway
    assert option.has_ferry
    assert option.raw["provider"] == "sample"


def test_parse_route_text_supports_vietnamese_flags() -> None:
    option = parse_route_text(
        "CT01\n10 km\n20 phút\nthu phí cao tốc phà",
        provider="sample",
    )

    assert option is not None
    assert option.has_toll
    assert option.has_highway
    assert option.has_ferry


def test_parse_route_text_returns_none_without_distance() -> None:
    assert parse_route_text(
        "Route\n20 min",
        provider="sample",
    ) is None


def test_parse_route_text_returns_none_without_duration() -> None:
    assert parse_route_text(
        "Route\n10 km",
        provider="sample",
    ) is None


def test_parse_route_text_returns_none_for_bad_distance_conversion() -> None:
    with patch.object(
        TextConverter,
        "distance_to_km",
        return_value=None,
    ):
        assert parse_route_text(
            "Route\n10 km\n20 min",
            provider="sample",
        ) is None


def test_parse_route_text_returns_none_for_bad_duration_conversion() -> None:
    with patch.object(
        TextConverter,
        "duration_to_minutes",
        return_value=None,
    ):
        assert parse_route_text(
            "Route\n10 km\n20 min",
            provider="sample",
        ) is None


def test_parse_route_text_allows_empty_summary() -> None:
    option = parse_route_text(
        "Distance: 10 km\nTime: 20 min",
        provider="sample",
    )

    assert option is not None
    assert option.summary == ""


def test_parse_route_text_skips_blank_line_before_summary() -> None:
    option = parse_route_text(
        "\n\nRoute A\n10 km\n20 min",
        provider="sample",
    )

    assert option is not None
    assert option.summary == "Route A"


def test_parse_route_text_normalizes_decomposed_vietnamese() -> None:
    option = parse_route_text(
        "Route\n2 giờ 46 phút\n127.2 km",
        provider="sample",
    )

    assert option is not None
    assert option.duration_minutes == 166
    assert option.distance_km == 127.2
