from dataclasses import FrozenInstanceError

import pytest

from app.presentation.app_metadata import AppMetadata


def test_default_metadata() -> None:
    metadata = AppMetadata()

    assert metadata.name == "DistanceCalculatorPro"
    assert metadata.version == "1.3.0-rc1"
    assert metadata.organization == "DistanceCalculatorPro"
    assert metadata.domain == "distancecalculatorpro.local"


def test_metadata_is_immutable() -> None:
    metadata = AppMetadata()

    with pytest.raises(FrozenInstanceError):
        metadata.name = "Changed"  # type: ignore[misc]
