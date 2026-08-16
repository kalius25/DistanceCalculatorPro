import pytest

from app.engines.bing_maps_url_builder import BingMapsUrlBuilder
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest


def test_build_driving_url() -> None:
    request = RouteRequest(
        origin="10.113922624804262,105.69436247381175",
        destination="10.892645,105.041044",
        travel_mode=TravelMode.DRIVING,
    )

    assert BingMapsUrlBuilder.build(request) == (
        "https://www.bing.com/maps/directions"
        "?style=r"
        "&rtp=pos.10.113922624804262_105.69436247381175"
        "~pos.10.892645_105.041044"
        "&mode=d"
    )


def test_build_walking_url() -> None:
    request = RouteRequest(
        origin="10.113922624804262,105.69436247381175",
        destination="10.892645,105.041044",
        travel_mode=TravelMode.WALKING,
    )

    assert BingMapsUrlBuilder.build(request).endswith("&mode=w")


def test_coordinate_removes_whitespace() -> None:
    assert BingMapsUrlBuilder.coordinate(
        " 10.113922624804262 , 105.69436247381175 "
    ) == "10.113922624804262_105.69436247381175"


def test_coordinate_accepts_bing_underscore_format() -> None:
    assert BingMapsUrlBuilder.coordinate(
        "10.113922624804262_105.69436247381175"
    ) == "10.113922624804262_105.69436247381175"


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("10.1", "must contain latitude and longitude"),
        ("10.1,", "must contain latitude and longitude"),
        ("north,east", "must be numeric"),
        ("91,105", "latitude must be between -90 and 90"),
        ("10,181", "longitude must be between -180 and 180"),
    ],
)
def test_coordinate_rejects_invalid_values(
    value: str,
    message: str,
) -> None:
    with pytest.raises(ValueError, match=message):
        BingMapsUrlBuilder.coordinate(value)


@pytest.mark.parametrize(
    "travel_mode",
    [
        TravelMode.BICYCLING,
        TravelMode.TRANSIT,
    ],
)
def test_mode_rejects_unsupported_modes(
    travel_mode: TravelMode,
) -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported Bing Maps travel mode",
    ):
        BingMapsUrlBuilder.mode(travel_mode)
