"""VietBanDo directions URL builder."""

from __future__ import annotations

import re

from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest

_BASE_URL = "https://maps.vietbando.com/maps/"
_MODE_BY_TRAVEL_MODE = {
    TravelMode.DRIVING: "2",
    TravelMode.TRUCK: "3",
    TravelMode.WALKING: "5",
}


class VietBanDoUrlBuilder:
    """Build VietBanDo web route URLs."""

    @staticmethod
    def build(request: RouteRequest) -> str:
        """Build one VietBanDo route URL."""
        origin = VietBanDoUrlBuilder.coordinate(request.origin)
        destination = VietBanDoUrlBuilder.coordinate(request.destination)
        mode = VietBanDoUrlBuilder.mode(request.travel_mode)

        return f"{_BASE_URL}" f"?fp={origin}|{destination};{mode};0;0,0"

    @staticmethod
    def coordinate(value: str) -> str:
        """Normalize to VietBanDo ``latitude,longitude`` form."""
        compact = re.sub(r"\s+", "", value)
        parts = compact.split(",")

        if len(parts) != 2 or not all(parts):
            raise ValueError(
                "VietBanDo coordinates must contain latitude and longitude."
            )

        try:
            latitude = float(parts[0])
            longitude = float(parts[1])
        except ValueError as error:
            raise ValueError(
                "VietBanDo latitude and longitude must be numeric."
            ) from error

        if not -90 <= latitude <= 90:
            raise ValueError("VietBanDo latitude must be between -90 and 90.")
        if not -180 <= longitude <= 180:
            raise ValueError("VietBanDo longitude must be between -180 and 180.")

        return f"{parts[0]},{parts[1]}"

    @staticmethod
    def mode(travel_mode: TravelMode) -> str:
        """Return the VietBanDo web mode token."""
        try:
            return _MODE_BY_TRAVEL_MODE[travel_mode]
        except KeyError as error:
            raise ValueError(
                "Unsupported VietBanDo travel mode: " f"{travel_mode.value}"
            ) from error


__all__ = ["VietBanDoUrlBuilder"]
