import warnings

from app.config import GOOGLE_LANGUAGE, GOOGLE_REGION
from app.engines.google_maps_url_builder import GoogleMapsUrlBuilder
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest


def make_request(**kwargs):
    data = dict(
        origin="10.762622,106.660172",
        destination="10.823099,106.629664",
        travel_mode=TravelMode.DRIVING,
        language=GOOGLE_LANGUAGE,
        region=GOOGLE_REGION,
    )
    data.update(kwargs)
    return RouteRequest(**data)


def test_build_path_based_directions_url():
    url = GoogleMapsUrlBuilder.build(make_request())
    assert url.startswith(
        "https://www.google.com/maps/dir/"
        "10.762622,106.660172/10.823099,106.629664/"
    )
    assert f"hl={GOOGLE_LANGUAGE}" in url
    assert f"gl={GOOGLE_REGION}" in url


def test_build_encodes_place_names_and_uses_defaults():
    request = make_request(
        origin="Ho Chi Minh City",
        destination="Cần Thơ",
        language="",
        region="",
    )
    url = GoogleMapsUrlBuilder.build(request)
    assert "Ho%20Chi%20Minh%20City" in url
    assert "C%E1%BA%A7n%20Th%C6%A1" in url
    assert f"hl={GOOGLE_LANGUAGE}" in url
    assert f"gl={GOOGLE_REGION}" in url


def test_build_search():
    url = GoogleMapsUrlBuilder.build_search("Ho Chi Minh")
    assert url == "https://www.google.com/maps/search/Ho%20Chi%20Minh/"


def test_build_route():
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        url = GoogleMapsUrlBuilder.build_route("Ho Chi Minh", "Can Tho")
    assert len(captured) == 1
    assert issubclass(captured[0].category, DeprecationWarning)
    assert "/Ho%20Chi%20Minh/Can%20Tho/" in url
