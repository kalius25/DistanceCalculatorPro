"""Validation rules for workbook route rows."""

from __future__ import annotations

from dataclasses import dataclass

from .models import RouteJobStatus


@dataclass(frozen=True, slots=True)
class RowValidation:
    """Validation outcome used by the row mapper."""

    status: RouteJobStatus
    message: str | None = None
    distance_km: float | None = None


class RowValidator:
    """Validate route endpoints without opening a browser."""

    def validate(self, origin: str, destination: str) -> RowValidation:
        if not origin or not destination:
            return RowValidation(
                RouteJobStatus.SKIPPED,
                "Origin and destination are required.",
            )

        if origin.casefold() == destination.casefold():
            return RowValidation(RouteJobStatus.DONE, distance_km=0.0)

        for field_name, value in (
            ("origin", origin),
            ("destination", destination),
        ):
            error = self._coordinate_error(value)
            if error is not None:
                return RowValidation(
                    RouteJobStatus.INVALID,
                    f"Invalid {field_name} coordinate: {error}",
                )

        return RowValidation(RouteJobStatus.PENDING)

    @staticmethod
    def _coordinate_error(value: str) -> str | None:
        parts = [part.strip() for part in value.split(",")]
        if len(parts) != 2:
            return None
        try:
            latitude, longitude = (float(part) for part in parts)
        except ValueError:
            return "latitude and longitude must be numeric"
        if not -90 <= latitude <= 90:
            return "latitude must be between -90 and 90"
        if not -180 <= longitude <= 180:
            return "longitude must be between -180 and 180"
        return None
