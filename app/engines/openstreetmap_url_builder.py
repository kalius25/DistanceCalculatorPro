"""OpenStreetMap directions URL builder."""

from __future__ import annotations

import re

from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest

_BASE_DIRECTIONS_URL = "https://www.openstreetmap.org/directions"

_ENGINE_BY_TRAVEL_MODE = {
    TravelMode.DRIVING: "fossgis_osrm_car",
    TravelMode.WALKING: "fossgis_osrm_foot",
}


class OpenStreetMapUrlBuilder:
    """Build OpenStreetMap web directions URLs."""

    @staticmethod
    def build(request: RouteRequest) -> str:
        """Build an OpenStreetMap directions URL for one request."""
        origin = OpenStreetMapUrlBuilder.coordinate(request.origin)
        destination = OpenStreetMapUrlBuilder.coordinate(
            request.destination
        )
        engine = OpenStreetMapUrlBuilder.engine(request.travel_mode)

        return (
            f"{_BASE_DIRECTIONS_URL}"
            f"?engine={engine}"
            f"&route={origin};{destination}"
        )

    @staticmethod
    def coordinate(value: str) -> str:
        """Normalize a coordinate to OSM ``latitude,longitude`` form."""
        compact = re.sub(r"\s+", "", value)
        parts = compact.split(",")

        if len(parts) != 2 or not all(parts):
            raise ValueError(
                "OpenStreetMap coordinates must contain latitude "
                "and longitude."
            )

        try:
            latitude = float(parts[0])
            longitude = float(parts[1])
        except ValueError as error:
            raise ValueError(
                "OpenStreetMap latitude and longitude must be numeric."
            ) from error

        if not -90 <= latitude <= 90:
            raise ValueError(
                "OpenStreetMap latitude must be between -90 and 90."
            )
        if not -180 <= longitude <= 180:
            raise ValueError(
                "OpenStreetMap longitude must be between -180 and 180."
            )

        return f"{parts[0]},{parts[1]}"

    @staticmethod
    def engine(travel_mode: TravelMode) -> str:
        """Return the OpenStreetMap routing-engine token."""
        try:
            return _ENGINE_BY_TRAVEL_MODE[travel_mode]
        except KeyError as error:
            raise ValueError(
                "Unsupported OpenStreetMap travel mode: "
                f"{travel_mode.value}"
            ) from error


__all__ = ["OpenStreetMapUrlBuilder"]
