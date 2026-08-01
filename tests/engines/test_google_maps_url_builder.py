import warnings

import pytest

from app.config import GOOGLE_LANGUAGE, GOOGLE_REGION
from app.engines.google_maps_url_builder import GoogleMapsUrlBuilder
from app.enums.route_preference import RoutePreference
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


@pytest.mark.parametrize(
    ("mode", "ferry", "toll", "highway", "expected"),
    [
        (TravelMode.DRIVING, False, False, False, "!4m2!4m1!3e0"),
        (TravelMode.DRIVING, True, False, False, "!4m4!4m3!2m1!3b1!3e0"),
        (TravelMode.DRIVING, False, True, False, "!4m4!4m3!2m1!2b1!3e0"),
        (TravelMode.DRIVING, False, False, True, "!4m4!4m3!2m1!1b1!3e0"),
        (TravelMode.DRIVING, True, True, False, "!4m5!4m4!2m2!2b1!3b1!3e0"),
        (TravelMode.DRIVING, True, False, True, "!4m5!4m4!2m2!1b1!3b1!3e0"),
        (TravelMode.DRIVING, False, True, True, "!4m5!4m4!2m2!1b1!2b1!3e0"),
        (TravelMode.DRIVING, True, True, True, "!4m6!4m5!2m3!1b1!2b1!3b1!3e0"),
        (TravelMode.WALKING, False, False, False, "!4m2!4m1!3e2"),
        (TravelMode.WALKING, True, False, False, "!4m4!4m3!2m1!3b1!3e2"),
    ],
)
def test_build_maps_route_options_to_data_fragment(
    mode, ferry, toll, highway, expected
):
    avoid = RoutePreference.AVOID
    automatic = RoutePreference.AUTO
    request = make_request(
        travel_mode=mode,
        ferry_preference=avoid if ferry else automatic,
        toll_preference=avoid if toll else automatic,
        highway_preference=avoid if highway else automatic,
    )

    url = GoogleMapsUrlBuilder.build(request)

    assert f"/data={expected}/?" in url


def test_build_path_based_directions_url():
    url = GoogleMapsUrlBuilder.build(make_request())
    assert url.startswith(
        "https://www.google.com/maps/dir/"
        "10.762622,106.660172/10.823099,106.629664/"
        "data=!4m2!4m1!3e0/"
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


def test_build_rejects_unmapped_route_option_combination():
    request = make_request(
        travel_mode=TravelMode.WALKING,
        toll_preference=RoutePreference.AVOID,
    )

    with pytest.raises(
        ValueError,
        match="Unsupported Google Maps route option combination",
    ):
        GoogleMapsUrlBuilder.build(request)


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
    assert "/data=!4m2!4m1!3e0/" in url
