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
        ProviderType.VIETBANDO_WEB,
    )


def test_existing_v1_3_providers_remain_executable() -> None:
    for provider in (
        ProviderType.GOOGLE_MAPS_WEB,
        ProviderType.BING_MAPS_WEB,
        ProviderType.OPENSTREETMAP_WEB,
    ):
        definition = provider_definition(provider)
        assert definition.engine_ready
        assert definition.execution_enabled
        assert definition.roadmap_sprint is None


def test_vietbando_is_executable_after_sprint_3_7b() -> None:
    definition = provider_definition(ProviderType.VIETBANDO_WEB)

    assert definition.engine_ready
    assert definition.execution_enabled
    assert definition.roadmap_sprint is None


def test_provider_travel_mode_capabilities() -> None:
    standard = (
        TravelMode.DRIVING,
        TravelMode.WALKING,
    )
    for provider in (
        ProviderType.GOOGLE_MAPS_WEB,
        ProviderType.BING_MAPS_WEB,
        ProviderType.OPENSTREETMAP_WEB,
    ):
        assert provider_definition(provider).supported_travel_modes == standard

    assert provider_definition(ProviderType.VIETBANDO_WEB).supported_travel_modes == (
        TravelMode.DRIVING,
        TravelMode.TRUCK,
        TravelMode.WALKING,
    )


def test_route_preferences_remain_google_only_in_sprint_3_3() -> None:
    google = provider_definition(ProviderType.GOOGLE_MAPS_WEB)
    bing = provider_definition(ProviderType.BING_MAPS_WEB)
    osm = provider_definition(ProviderType.OPENSTREETMAP_WEB)
    vietbando = provider_definition(ProviderType.VIETBANDO_WEB)

    assert google.supports_avoid_tolls
    assert google.supports_avoid_highways
    assert google.supports_avoid_ferries

    for definition in (bing, osm, vietbando):
        assert not definition.supports_avoid_tolls
        assert not definition.supports_avoid_highways
        assert not definition.supports_avoid_ferries
