from app.parsers.google_maps_parser import (
    _extract_distance,
    _extract_duration,
    _extract_summary,
    _has_keyword,
)


# ==========================================================
# _has_keyword
# ==========================================================


def test_has_keyword_true():
    assert _has_keyword(
        "Có thu phí",
        ("thu phí",),
    )


def test_has_keyword_false():
    assert not _has_keyword(
        "Quốc lộ 1A",
        ("thu phí",),
    )


def test_has_keyword_ignore_case():
    assert _has_keyword(
        "TOLL ROAD",
        ("toll",),
    )


# ==========================================================
# _extract_distance
# ==========================================================


def test_extract_distance_km():
    assert _extract_distance("125 km") == "125 km"


def test_extract_distance_meter():
    assert _extract_distance("950 m") == "950 m"


def test_extract_distance_mile():
    assert _extract_distance("2.5 mi") == "2.5 mi"


def test_extract_distance_feet():
    assert _extract_distance("1200 ft") == "1200 ft"


def test_extract_distance_none():
    assert _extract_distance("Không có khoảng cách") is None


# ==========================================================
# _extract_duration
# ==========================================================


def test_extract_duration_hour():
    assert _extract_duration("2 giờ") == "2 giờ"


def test_extract_duration_hour_minute():
    assert _extract_duration("2 giờ 15 phút") == "2 giờ 15 phút"


def test_extract_duration_minute():
    assert _extract_duration("35 phút") == "35 phút"


def test_extract_duration_english():
    assert _extract_duration("1 hr 25 min") == "1 hr 25 min"


def test_extract_duration_none():
    assert _extract_duration("Không có thời gian") is None


# ==========================================================
# _extract_summary
# ==========================================================


def test_extract_summary_simple():
    text = """
QL1A

2 giờ

125 km
"""

    assert _extract_summary(text) == "QL1A"


def test_extract_summary_skip_distance():
    text = """
125 km

QL60

2 giờ
"""

    assert _extract_summary(text) == "QL60"


def test_extract_summary_skip_duration():
    text = """
2 giờ

QL80
"""

    assert _extract_summary(text) == "QL80"


def test_extract_summary_skip_toll():
    text = """
Thu phí

QL1A
"""

    assert _extract_summary(text) == "QL1A"


def test_extract_summary_empty():
    assert _extract_summary("") == ""