import pytest

from app.parsers.google_maps_parser import _extract_distance, _parse_text

# ==========================================================
# Happy Path
# ==========================================================


def test_parse_text_simple_route():
    text = """
QL1A

2 giờ 15 phút

125 km
"""

    route = _parse_text(text)

    assert route is not None
    assert route.summary == "QL1A"
    assert route.distance_text == "125 km"
    assert route.distance_km == 125
    assert route.duration_text == "2 giờ 15 phút"
    assert route.duration_minutes == 135
    assert route.has_toll is False
    assert route.has_ferry is False
    assert route.has_highway is False


def test_parse_text_with_toll():
    text = """
QL1A

2 giờ

120 km

Có thu phí
"""

    route = _parse_text(text)

    assert route is not None
    assert route.has_toll is True
    assert route.has_ferry is False
    assert route.has_highway is False


def test_parse_text_with_ferry():
    text = """
Qua phà

35 phút

12 km
"""

    route = _parse_text(text)

    assert route is not None
    assert route.has_ferry is True


def test_parse_text_with_highway():
    text = """
CT01

1 giờ

85 km

Đi theo cao tốc
"""

    route = _parse_text(text)

    assert route is not None
    assert route.has_highway is True


# ==========================================================
# English
# ==========================================================


def test_parse_text_english():
    text = """
Highway 1

1 hr 30 min

80 mi

Toll road
"""

    route = _parse_text(text)

    assert route is not None
    assert route.summary == "Highway 1"
    assert route.duration_minutes == 90
    assert route.has_toll is True
    assert route.has_highway is True

    # khoảng 128.74752 km
    assert route.distance_km == pytest.approx(128.74752)


# ==========================================================
# Raw Data
# ==========================================================


def test_parse_text_raw_dictionary():
    text = """
QL1A

2 giờ

100 km
"""

    route = _parse_text(text)

    assert route is not None

    assert route.raw["text"] == text
    assert route.raw["summary"] == "QL1A"
    assert route.raw["distance_text"] == "100 km"
    assert route.raw["duration_text"] == "2 giờ"


# ==========================================================
# Invalid
# ==========================================================


@pytest.mark.parametrize(
    "text",
    [
        "",
        "QL1A",
        "100 km",
        "2 giờ",
        "Không có dữ liệu",
    ],
)
def test_parse_text_invalid(text):
    assert _parse_text(text) is None


def test_parse_text_invalid_distance():
    text = """
QL1A

2 giờ

abc km
"""

    assert _parse_text(text) is None


def test_parse_text_invalid_duration():
    text = """
QL1A

abc giờ

100 km
"""

    assert _parse_text(text) is None


# ==========================================================
# Summary
# ==========================================================


def test_parse_text_summary_skip_distance():
    text = """
100 km

QL80

2 giờ
"""

    route = _parse_text(text)

    assert route is not None
    assert route.summary == "QL80"


def test_parse_text_summary_skip_toll():
    text = """
Thu phí

QL1A

2 giờ

120 km
"""

    route = _parse_text(text)

    assert route is not None
    assert route.summary == "QL1A"


def test_extract_distance_after_duration():
    text = """
1 hr 30 min

80 mi
"""

    assert _extract_distance(text) == "80 mi"
