from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode
from app.providers.catalog import (
    PROVIDER_DEFINITIONS,
    provider_definition,
)


def test_provider_catalog_contains_v1_3_providers() -> None:
    assert tuple(definition.provider for definition in PROVIDER_DEFINITIONS) == (
        ProviderType.GOOGLE_MAPS_WEB,
        ProviderType.BING_MAPS_WEB,
        ProviderType.OPENSTREETMAP_WEB,
    )


def test_all_v1_3_providers_are_executable_in_sprint_3_5() -> None:
    for definition in PROVIDER_DEFINITIONS:
        assert definition.engine_ready
        assert definition.execution_enabled
        assert definition.roadmap_sprint is None


def test_provider_foundation_supports_driving_and_walking() -> None:
    expected = (
        TravelMode.DRIVING,
        TravelMode.WALKING,
    )

    for definition in PROVIDER_DEFINITIONS:
        assert definition.supported_travel_modes == expected


def test_route_preferences_remain_google_only_in_sprint_3_3() -> None:
    google = provider_definition(ProviderType.GOOGLE_MAPS_WEB)
    bing = provider_definition(ProviderType.BING_MAPS_WEB)
    osm = provider_definition(ProviderType.OPENSTREETMAP_WEB)

    assert google.supports_avoid_tolls
    assert google.supports_avoid_highways
    assert google.supports_avoid_ferries

    for definition in (bing, osm):
        assert not definition.supports_avoid_tolls
        assert not definition.supports_avoid_highways
        assert not definition.supports_avoid_ferries
