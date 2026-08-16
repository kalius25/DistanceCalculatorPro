"""Bing Maps directions URL builder."""

from __future__ import annotations

import re

from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest

_BASE_DIRECTIONS_URL = "https://www.bing.com/maps/directions"

_MODE_BY_TRAVEL_MODE = {
    TravelMode.DRIVING: "d",
    TravelMode.WALKING: "w",
}


class BingMapsUrlBuilder:
    """Build Bing Maps web directions URLs."""

    @staticmethod
    def build(request: RouteRequest) -> str:
        """Build a Bing Maps directions URL for one route request."""
        origin = BingMapsUrlBuilder.coordinate(request.origin)
        destination = BingMapsUrlBuilder.coordinate(request.destination)
        mode = BingMapsUrlBuilder.mode(request.travel_mode)

        return (
            f"{_BASE_DIRECTIONS_URL}"
            f"?style=r"
            f"&rtp=pos.{origin}~pos.{destination}"
            f"&mode={mode}"
        )

    @staticmethod
    def coordinate(value: str) -> str:
        """Normalize ``latitude,longitude`` to Bing ``latitude_longitude``."""
        compact = re.sub(r"\s+", "", value)
        normalized = compact.replace(",", "_")
        parts = normalized.split("_")

        if len(parts) != 2 or not all(parts):
            raise ValueError(
                "Bing Maps coordinates must contain latitude and longitude."
            )

        try:
            latitude = float(parts[0])
            longitude = float(parts[1])
        except ValueError as error:
            raise ValueError(
                "Bing Maps latitude and longitude must be numeric."
            ) from error

        if not -90 <= latitude <= 90:
            raise ValueError("Bing Maps latitude must be between -90 and 90.")
        if not -180 <= longitude <= 180:
            raise ValueError("Bing Maps longitude must be between -180 and 180.")

        return f"{parts[0]}_{parts[1]}"

    @staticmethod
    def mode(travel_mode: TravelMode) -> str:
        """Return the Bing Maps web mode token."""
        try:
            return _MODE_BY_TRAVEL_MODE[travel_mode]
        except KeyError as error:
            raise ValueError(
                "Unsupported Bing Maps travel mode: " f"{travel_mode.value}"
            ) from error


__all__ = ["BingMapsUrlBuilder"]
