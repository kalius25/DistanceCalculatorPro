import pytest

from app.engines.vietbando_url_builder import VietBanDoUrlBuilder
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest


@pytest.mark.parametrize(
    ("travel_mode", "mode"),
    [
        (TravelMode.DRIVING, "2"),
        (TravelMode.TRUCK, "3"),
        (TravelMode.WALKING, "5"),
    ],
)
def test_build_url_for_supported_modes(
    travel_mode: TravelMode,
    mode: str,
) -> None:
    request = RouteRequest(
        origin="10.113922624804262,105.69436247381175",
        destination="10.892645,105.041044",
        travel_mode=travel_mode,
    )

    assert VietBanDoUrlBuilder.build(request) == (
        "https://maps.vietbando.com/maps/"
        "?fp=10.113922624804262,105.69436247381175"
        "|10.892645,105.041044"
        f";{mode};0;0,0"
    )


def test_coordinate_removes_whitespace() -> None:
    assert (
        VietBanDoUrlBuilder.coordinate(" 10.113922624804262 , 105.69436247381175 ")
        == "10.113922624804262,105.69436247381175"
    )


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
        VietBanDoUrlBuilder.coordinate(value)


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
        match="Unsupported VietBanDo travel mode",
    ):
        VietBanDoUrlBuilder.mode(travel_mode)
