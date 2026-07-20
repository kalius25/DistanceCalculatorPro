from __future__ import annotations

import pytest

from app.utils.text_converter import TextConverter


# ==========================================================
# distance_to_km()
# ==========================================================

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 km", 1.0),
        ("2 km", 2.0),
        ("2.5 km", 2.5),
        ("2,5 km", 2.5),
        ("0.5 km", 0.5),
        ("999 m", 0.999),
        ("500 m", 0.5),
        ("1000 m", 1.0),
    ],
)
def test_distance_to_km_metric(text: str, expected: float) -> None:
    assert TextConverter.distance_to_km(text) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 mi", 1.609344),
        ("2 mi", 3.218688),
        ("0.5 mi", 0.804672),
    ],
)
def test_distance_to_km_mile(text: str, expected: float) -> None:
    assert TextConverter.distance_to_km(text) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1000 ft", 0.3048),
        ("500 ft", 0.1524),
    ],
)
def test_distance_to_km_feet(text: str, expected: float) -> None:
    assert TextConverter.distance_to_km(text) == pytest.approx(expected)


@pytest.mark.parametrize(
    "text",
    [
        None,
        "",
        " ",
        "abc",
        "123",
        "km",
        "1",
        "1 meter",
        "1mile",
        "10 yd",
    ],
)
def test_distance_to_km_invalid(text: str | None) -> None:
    assert TextConverter.distance_to_km(text) is None


# ==========================================================
# duration_to_minutes()
# ==========================================================

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 phút", 1),
        ("30 phút", 30),
        ("45 p", 45),
        ("45 ph", 45),
        ("45 min", 45),
        ("45 mins", 45),
        ("45 minute", 45),
        ("45 minutes", 45),
    ],
)
def test_duration_minutes_only(text: str, expected: int) -> None:
    assert TextConverter.duration_to_minutes(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 giờ", 60),
        ("2 giờ", 120),
        ("3 tiếng", 180),
        ("1 h", 60),
        ("2 hr", 120),
        ("2 hrs", 120),
        ("1 hour", 60),
        ("2 hours", 120),
    ],
)
def test_duration_hours_only(text: str, expected: int) -> None:
    assert TextConverter.duration_to_minutes(text) == expected


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 giờ 15 phút", 75),
        ("2 giờ 5 phút", 125),
        ("2 giờ 30 p", 150),
        ("1 hr 30 min", 90),
        ("2 hrs 15 mins", 135),
        ("1 hour 45 minutes", 105),
    ],
)
def test_duration_hours_and_minutes(text: str, expected: int) -> None:
    assert TextConverter.duration_to_minutes(text) == expected


@pytest.mark.parametrize(
    "text",
    [
        None,
        "",
        " ",
        "abc",
        "123",
        "0 phút",
        "0 giờ",
        "0 hr",
    ],
)
def test_duration_invalid(text: str | None) -> None:
    assert TextConverter.duration_to_minutes(text) is None

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("   1 km", 1.0),
        ("1 km   ", 1.0),
        ("   1 km   ", 1.0),
    ],
)
def test_distance_trim(text: str, expected: float) -> None:
    assert TextConverter.distance_to_km(text) == pytest.approx(expected)

@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1 KM", 1.0),
        ("1 Mi", 1.609344),
        ("100 FT", 0.03048),
        ("2 HR", 120),
        ("30 MIN", 30),
    ],
)
def test_ignore_case(text: str, expected: float | int) -> None:
    assert (
        TextConverter.distance_to_km(text)
        or TextConverter.duration_to_minutes(text)
    ) == pytest.approx(expected)