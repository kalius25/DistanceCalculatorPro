"""Google Maps URL builder."""

from __future__ import annotations

import warnings
from urllib.parse import quote

from app.config import GOOGLE_LANGUAGE, GOOGLE_REGION
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest

_BASE_DIRECTIONS_URL = "https://www.google.com/maps/dir"


class GoogleMapsUrlBuilder:
    """Build Google Maps URLs."""

    @staticmethod
    def build(request: RouteRequest) -> str:
        """Build a path-based Google Maps Directions URL."""
        origin = quote(request.origin.strip(), safe=",")
        destination = quote(request.destination.strip(), safe=",")
        language = request.language or GOOGLE_LANGUAGE
        region = request.region or GOOGLE_REGION

        return (
            f"{_BASE_DIRECTIONS_URL}/{origin}/{destination}/"
            f"?hl={language}&gl={region}"
        )

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
