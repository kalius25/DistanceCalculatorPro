from unittest.mock import MagicMock

from app.providers.bing_web_provider import BingWebProvider
from app.providers.openstreetmap_web_provider import OpenStreetMapWebProvider


def test_bing_provider_uses_bing_result_identity() -> None:
    provider = BingWebProvider(MagicMock(), MagicMock())

    assert provider.PROVIDER_NAME == "bing_maps_web"


def test_osm_provider_uses_osm_result_identity() -> None:
    provider = OpenStreetMapWebProvider(MagicMock(), MagicMock())

    assert provider.PROVIDER_NAME == "openstreetmap_web"
