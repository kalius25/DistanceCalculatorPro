import pytest

from app.engines.openstreetmap_url_builder import (
    OpenStreetMapUrlBuilder,
)
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest


def test_build_driving_url() -> None:
    request = RouteRequest(
        origin="10.113922624804262,105.69436247381175",
        destination="10.892645,105.041044",
        travel_mode=TravelMode.DRIVING,
    )

    assert OpenStreetMapUrlBuilder.build(request) == (
        "https://www.openstreetmap.org/directions"
        "?engine=fossgis_osrm_car"
        "&route=10.113922624804262,105.69436247381175"
        ";10.892645,105.041044"
    )


def test_build_walking_url() -> None:
    request = RouteRequest(
        origin="10.113922624804262,105.69436247381175",
        destination="10.892645,105.041044",
        travel_mode=TravelMode.WALKING,
    )

    assert OpenStreetMapUrlBuilder.build(request).startswith(
        "https://www.openstreetmap.org/directions"
        "?engine=fossgis_osrm_foot&route="
    )


def test_coordinate_removes_whitespace() -> None:
    assert OpenStreetMapUrlBuilder.coordinate(
        " 10.113922624804262 , 105.69436247381175 "
    ) == "10.113922624804262,105.69436247381175"


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
        OpenStreetMapUrlBuilder.coordinate(value)


@pytest.mark.parametrize(
    "travel_mode",
    [
        TravelMode.BICYCLING,
        TravelMode.TRANSIT,
    ],
)
def test_engine_rejects_unsupported_modes(
    travel_mode: TravelMode,
) -> None:
    with pytest.raises(
        ValueError,
        match="Unsupported OpenStreetMap travel mode",
    ):
        OpenStreetMapUrlBuilder.engine(travel_mode)
