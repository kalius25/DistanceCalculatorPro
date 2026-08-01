"""Google Maps URL builder."""

from __future__ import annotations

import warnings
from urllib.parse import quote

from app.config import GOOGLE_LANGUAGE, GOOGLE_REGION
from app.enums.route_preference import RoutePreference
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest

_BASE_DIRECTIONS_URL = "https://www.google.com/maps/dir"

_ROUTE_DATA: dict[tuple[TravelMode, bool, bool, bool], str] = {
    (TravelMode.DRIVING, False, False, False): "!4m2!4m1!3e0",
    (TravelMode.DRIVING, True, False, False): "!4m4!4m3!2m1!3b1!3e0",
    (TravelMode.DRIVING, False, True, False): "!4m4!4m3!2m1!2b1!3e0",
    (TravelMode.DRIVING, False, False, True): "!4m4!4m3!2m1!1b1!3e0",
    (TravelMode.DRIVING, True, True, False): "!4m5!4m4!2m2!2b1!3b1!3e0",
    (TravelMode.DRIVING, True, False, True): "!4m5!4m4!2m2!1b1!3b1!3e0",
    (TravelMode.DRIVING, False, True, True): "!4m5!4m4!2m2!1b1!2b1!3e0",
    (TravelMode.DRIVING, True, True, True): "!4m6!4m5!2m3!1b1!2b1!3b1!3e0",
    (TravelMode.WALKING, False, False, False): "!4m2!4m1!3e2",
    (TravelMode.WALKING, True, False, False): "!4m4!4m3!2m1!3b1!3e2",
}


class GoogleMapsUrlBuilder:
    """Build Google Maps URLs."""

    @staticmethod
    def build(request: RouteRequest) -> str:
        """Build a path-based Google Maps Directions URL."""
        origin = quote(request.origin.strip(), safe=",")
        destination = quote(request.destination.strip(), safe=",")
        language = request.language or GOOGLE_LANGUAGE
        region = request.region or GOOGLE_REGION
        route_data = GoogleMapsUrlBuilder.route_data(request)

        return (
            f"{_BASE_DIRECTIONS_URL}/{origin}/{destination}/"
            f"data={route_data}/?hl={language}&gl={region}"
        )

    @staticmethod
    def route_data(request: RouteRequest) -> str:
        """Return the Google Maps data fragment for one request."""
        avoid_ferries = request.ferry_preference is RoutePreference.AVOID
        avoid_tolls = request.toll_preference is RoutePreference.AVOID
        avoid_highways = request.highway_preference is RoutePreference.AVOID
        key = (
            request.travel_mode,
            avoid_ferries,
            avoid_tolls,
            avoid_highways,
        )
        try:
            return _ROUTE_DATA[key]
        except KeyError as error:
            raise ValueError(
                "Unsupported Google Maps route option combination: "
                f"mode={request.travel_mode.value}, "
                f"avoid_ferries={avoid_ferries}, "
                f"avoid_tolls={avoid_tolls}, "
                f"avoid_highways={avoid_highways}"
            ) from error

    @staticmethod
    def build_search(keyword: str) -> str:
        """Build a Google Maps Search URL."""
        encoded = quote(keyword.strip(), safe="")
        return f"https://www.google.com/maps/search/{encoded}/"

    @staticmethod
    def build_route(
        origin: str,
        destination: str,
        travel_mode: str = "driving",
    ) -> str:
        """Build a deprecated route URL for backward compatibility."""
        warnings.warn(
            (
                "GoogleMapsUrlBuilder.build_route() is deprecated and will "
                "be removed in a future version. "
                "Use GoogleMapsUrlBuilder.build(RouteRequest) instead."
            ),
            category=DeprecationWarning,
            stacklevel=2,
        )
        request = RouteRequest(
            origin=origin,
            destination=destination,
            travel_mode=TravelMode(travel_mode),
            language=GOOGLE_LANGUAGE,
            region=GOOGLE_REGION,
        )
        return GoogleMapsUrlBuilder.build(request)
