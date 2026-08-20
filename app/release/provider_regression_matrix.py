"""Release regression capability matrix for production providers."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode


@dataclass(frozen=True, slots=True)
class ProviderRegressionCase:
    provider: ProviderType
    travel_mode: TravelMode
    duration_required: bool


PROVIDER_REGRESSION_CASES: tuple[ProviderRegressionCase, ...] = (
    ProviderRegressionCase(
        ProviderType.GOOGLE_MAPS_WEB,
        TravelMode.DRIVING,
        True,
    ),
    ProviderRegressionCase(
        ProviderType.GOOGLE_MAPS_WEB,
        TravelMode.WALKING,
        True,
    ),
    ProviderRegressionCase(
        ProviderType.BING_MAPS_WEB,
        TravelMode.DRIVING,
        True,
    ),
    ProviderRegressionCase(
        ProviderType.BING_MAPS_WEB,
        TravelMode.WALKING,
        True,
    ),
    ProviderRegressionCase(
        ProviderType.OPENSTREETMAP_WEB,
        TravelMode.DRIVING,
        True,
    ),
    ProviderRegressionCase(
        ProviderType.OPENSTREETMAP_WEB,
        TravelMode.WALKING,
        True,
    ),
    ProviderRegressionCase(
        ProviderType.VIETBANDO_WEB,
        TravelMode.DRIVING,
        False,
    ),
    ProviderRegressionCase(
        ProviderType.VIETBANDO_WEB,
        TravelMode.TRUCK,
        False,
    ),
    ProviderRegressionCase(
        ProviderType.VIETBANDO_WEB,
        TravelMode.WALKING,
        False,
    ),
)


def duration_matches_capability(
    value: object,
    *,
    required: bool,
) -> bool:
    """Validate an output duration cell against provider capability."""
    if required:
        return value not in (None, "")
    return value in (None, "")


def distance_is_success(value: object) -> bool:
    """Return whether an output distance cell contains a real result."""
    if value in (None, ""):
        return False
    if isinstance(value, str) and value.lstrip().startswith("ERROR:"):
        return False
    return True


__all__ = [
    "PROVIDER_REGRESSION_CASES",
    "ProviderRegressionCase",
    "distance_is_success",
    "duration_matches_capability",
]
