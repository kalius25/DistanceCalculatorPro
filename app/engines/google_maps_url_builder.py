"""
Google Maps URL builder.
"""

from __future__ import annotations

import warnings
from urllib.parse import quote_plus

from app.config import (
    GOOGLE_LANGUAGE,
    GOOGLE_MAPS_DIRECTIONS_URL,
    GOOGLE_MAPS_SEARCH_URL,
    GOOGLE_REGION,
)
from app.enums.route_preference import RoutePreference
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest


class GoogleMapsUrlBuilder:
    """Build Google Maps URLs."""

    @staticmethod
    def build(request: RouteRequest) -> str:
        """
        Build a Google Maps Directions URL from a RouteRequest.
        """

        origin = quote_plus(request.origin)
        destination = quote_plus(request.destination)

        url = (
            f"{GOOGLE_MAPS_DIRECTIONS_URL}"
            f"&origin={origin}"
            f"&destination={destination}"
            f"&travelmode={request.travel_mode.value}"
            f"&hl={request.language or GOOGLE_LANGUAGE}"
            f"&gl={request.region or GOOGLE_REGION}"
        )

        avoid: list[str] = []

        if request.toll_preference is RoutePreference.AVOID:
            avoid.append("tolls")

        if request.highway_preference is RoutePreference.AVOID:
            avoid.append("highways")

        if request.ferry_preference is RoutePreference.AVOID:
            avoid.append("ferries")

        if avoid:
            url += "&avoid=" + ",".join(avoid)

        return url

    @staticmethod
    def build_search(keyword: str) -> str:
        """
        Build a Google Maps Search URL.
        """

        keyword = quote_plus(keyword)

        return f"{GOOGLE_MAPS_SEARCH_URL}?api=1&query={keyword}"

    @staticmethod
    def build_route(
        origin: str,
        destination: str,
        travel_mode: str = "driving",
    ) -> str:
        """
        Deprecated.

        This method is kept only for backward compatibility.
        New code should use build(RouteRequest).
        """

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
