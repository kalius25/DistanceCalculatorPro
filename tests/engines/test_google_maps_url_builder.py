import warnings

from app.config import GOOGLE_LANGUAGE
from app.config import GOOGLE_REGION
from app.engines.google_maps_url_builder import GoogleMapsUrlBuilder
from app.enums.route_preference import RoutePreference
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest


def make_request(**kwargs):
    data = dict(
        origin="Ho Chi Minh",
        destination="Can Tho",
        travel_mode=TravelMode.DRIVING,
        language=GOOGLE_LANGUAGE,
        region=GOOGLE_REGION,
        toll_preference=RoutePreference.AUTO,
        highway_preference=RoutePreference.AUTO,
        ferry_preference=RoutePreference.AUTO,
    )
    data.update(kwargs)
    return RouteRequest(**data)


def test_build_basic():
    request = make_request()

    url = GoogleMapsUrlBuilder.build(request)

    assert "origin=Ho+Chi+Minh" in url
    assert "destination=Can+Tho" in url
    assert "travelmode=driving" in url
    assert "&avoid=" not in url


def test_build_default_language_region():
    request = make_request(
        language="",
        region="",
    )

    url = GoogleMapsUrlBuilder.build(request)

    assert f"hl={GOOGLE_LANGUAGE}" in url
    assert f"gl={GOOGLE_REGION}" in url


def test_build_avoid_tolls():
    request = make_request(
        toll_preference=RoutePreference.AVOID,
    )

    url = GoogleMapsUrlBuilder.build(request)

    assert "avoid=tolls" in url
    assert "highways" not in url
    assert "ferries" not in url


def test_build_avoid_all():
    request = make_request(
        toll_preference=RoutePreference.AVOID,
        highway_preference=RoutePreference.AVOID,
        ferry_preference=RoutePreference.AVOID,
    )

    url = GoogleMapsUrlBuilder.build(request)

    assert "avoid=tolls,highways,ferries" in url


def test_build_search():
    url = GoogleMapsUrlBuilder.build_search("Ho Chi Minh")

    assert "query=Ho+Chi+Minh" in url


def test_build_route():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")

        url = GoogleMapsUrlBuilder.build_route(
            "Ho Chi Minh",
            "Can Tho",
        )

    assert len(w) == 1
    assert issubclass(w[0].category, DeprecationWarning)

    assert "origin=Ho+Chi+Minh" in url
    assert "destination=Can+Tho" in url