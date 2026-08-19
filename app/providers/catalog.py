"""Provider metadata used by presentation and execution guards."""

from __future__ import annotations

from dataclasses import dataclass

from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode


@dataclass(frozen=True, slots=True)
class ProviderDefinition:
    """Static capabilities for one route provider."""

    provider: ProviderType
    display_name: str
    supported_travel_modes: tuple[TravelMode, ...]
    engine_ready: bool
    execution_enabled: bool
    supports_avoid_tolls: bool
    supports_avoid_highways: bool
    supports_avoid_ferries: bool
    roadmap_sprint: str | None = None


PROVIDER_DEFINITIONS = (
    ProviderDefinition(
        provider=ProviderType.GOOGLE_MAPS_WEB,
        display_name="Google Maps Web",
        supported_travel_modes=(
            TravelMode.DRIVING,
            TravelMode.WALKING,
        ),
        engine_ready=True,
        execution_enabled=True,
        supports_avoid_tolls=True,
        supports_avoid_highways=True,
        supports_avoid_ferries=True,
    ),
    ProviderDefinition(
        provider=ProviderType.BING_MAPS_WEB,
        display_name="Bing Maps",
        supported_travel_modes=(
            TravelMode.DRIVING,
            TravelMode.WALKING,
        ),
        engine_ready=True,
        execution_enabled=True,
        supports_avoid_tolls=False,
        supports_avoid_highways=False,
        supports_avoid_ferries=False,
    ),
    ProviderDefinition(
        provider=ProviderType.OPENSTREETMAP_WEB,
        display_name="OpenStreetMap",
        supported_travel_modes=(
            TravelMode.DRIVING,
            TravelMode.WALKING,
        ),
        engine_ready=True,
        execution_enabled=True,
        supports_avoid_tolls=False,
        supports_avoid_highways=False,
        supports_avoid_ferries=False,
    ),
    ProviderDefinition(
        provider=ProviderType.VIETBANDO_WEB,
        display_name="VietBanDo",
        supported_travel_modes=(
            TravelMode.DRIVING,
            TravelMode.TRUCK,
            TravelMode.WALKING,
        ),
        engine_ready=True,
        execution_enabled=True,
        supports_avoid_tolls=False,
        supports_avoid_highways=False,
        supports_avoid_ferries=False,
    ),
)

_PROVIDER_DEFINITIONS_BY_TYPE = {
    definition.provider: definition for definition in PROVIDER_DEFINITIONS
}


def provider_definition(provider: ProviderType) -> ProviderDefinition:
    """Return the static definition for a provider."""
    return _PROVIDER_DEFINITIONS_BY_TYPE[provider]
