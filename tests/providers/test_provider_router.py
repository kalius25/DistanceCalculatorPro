from unittest.mock import MagicMock

import pytest

from app.enums.provider_type import ProviderType
from app.exceptions.provider_exception import ProviderException
from app.models.route_request import RouteRequest
from app.providers.provider_router import ProviderRouter


def _request(provider: object = ProviderType.BING_MAPS_WEB) -> RouteRequest:
    return RouteRequest(
        origin="A",
        destination="B",
        metadata={"provider": provider},
    )


def test_providers_returns_copy() -> None:
    provider = MagicMock()
    router = ProviderRouter({ProviderType.BING_MAPS_WEB: provider})

    providers = router.providers
    providers.clear()

    assert router.providers == {
        ProviderType.BING_MAPS_WEB: provider,
    }


def test_batch_lazily_starts_only_selected_provider() -> None:
    google = MagicMock()
    bing = MagicMock()
    expected = MagicMock()
    bing.calculate.return_value = expected
    router = ProviderRouter(
        {
            ProviderType.GOOGLE_MAPS_WEB: google,
            ProviderType.BING_MAPS_WEB: bing,
        }
    )

    router.start_batch()
    result = router.calculate(_request())
    router.calculate(_request())
    router.finish_batch()

    assert result is expected
    google.start_batch.assert_not_called()
    bing.start_batch.assert_called_once_with()
    assert bing.calculate.call_count == 2
    bing.finish_batch.assert_called_once_with()


def test_calculate_owns_batch_outside_explicit_batch() -> None:
    bing = MagicMock()
    expected = MagicMock()
    bing.calculate.return_value = expected
    router = ProviderRouter({ProviderType.BING_MAPS_WEB: bing})

    result = router.calculate(_request())

    assert result is expected
    bing.start_batch.assert_called_once_with()
    bing.finish_batch.assert_called_once_with()


def test_router_accepts_provider_string_metadata() -> None:
    bing = MagicMock()
    router = ProviderRouter({ProviderType.BING_MAPS_WEB: bing})

    router.calculate(_request("Bing Maps"))

    bing.calculate.assert_called_once()


def test_router_rejects_unknown_provider_string() -> None:
    router = ProviderRouter({})

    with pytest.raises(
        ProviderException,
        match="Unknown route provider: Missing Maps",
    ):
        router.calculate(_request("Missing Maps"))


def test_router_rejects_missing_provider_metadata() -> None:
    router = ProviderRouter({})
    request = RouteRequest(origin="A", destination="B")

    with pytest.raises(
        ProviderException,
        match="Route request does not specify a provider",
    ):
        router.calculate(request)


def test_router_rejects_unregistered_provider() -> None:
    router = ProviderRouter({})

    with pytest.raises(
        ProviderException,
        match="No production provider registered for Bing Maps",
    ):
        router.calculate(_request())


def test_finish_batch_is_safe_before_start() -> None:
    router = ProviderRouter({})

    router.finish_batch()

    assert not router._batch_started
