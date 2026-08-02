from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode
from app.presentation.workspace_configuration import (
    ColumnMapping,
    ProviderConfiguration,
    WorkspaceConfiguration,
)


def test_workspace_configuration_models_are_immutable_value_objects() -> None:
    mapping = ColumnMapping("Origin", "Destination", "Distance")
    provider = ProviderConfiguration(
        provider=ProviderType.GOOGLE_MAPS_WEB,
        travel_mode=TravelMode.DRIVING,
        avoid_tolls=True,
        avoid_highways=False,
        avoid_ferries=True,
    )

    configuration = WorkspaceConfiguration(mapping, provider)

    assert configuration.column_mapping == mapping
    assert configuration.provider_configuration == provider
    assert configuration.skip_existing_results
    assert provider.avoid_tolls
    assert not provider.avoid_highways
    assert provider.avoid_ferries
