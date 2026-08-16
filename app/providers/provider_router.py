"""Route calculation requests to the provider selected by the workspace."""

from __future__ import annotations

from collections.abc import Mapping

from app.enums.provider_type import ProviderType
from app.exceptions.provider_exception import ProviderException
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider

_PROVIDER_METADATA_KEY = "provider"


class ProviderRouter(BaseProvider):
    """Dispatch each request to its selected production provider."""

    def __init__(
        self,
        providers: Mapping[ProviderType, BaseProvider],
    ) -> None:
        self._providers = dict(providers)
        self._started: set[ProviderType] = set()
        self._batch_started = False

    @property
    def providers(self) -> dict[ProviderType, BaseProvider]:
        return dict(self._providers)

    def start_batch(self) -> None:
        self._batch_started = True
        self._started.clear()

    def finish_batch(self) -> None:
        for provider_type in tuple(self._started):
            self._providers[provider_type].finish_batch()
        self._started.clear()
        self._batch_started = False

    def calculate(self, request: RouteRequest) -> RouteResult:
        provider_type = self._provider_type(request)
        provider = self._providers.get(provider_type)
        if provider is None:
            raise ProviderException(
                f"No production provider registered for {provider_type.value}."
            )

        owns_batch = not self._batch_started
        if owns_batch:
            self.start_batch()

        try:
            if provider_type not in self._started:
                provider.start_batch()
                self._started.add(provider_type)
            return provider.calculate(request)
        finally:
            if owns_batch:
                self.finish_batch()

    @staticmethod
    def _provider_type(request: RouteRequest) -> ProviderType:
        value = request.metadata.get(_PROVIDER_METADATA_KEY)
        if isinstance(value, ProviderType):
            return value
        if isinstance(value, str):
            try:
                return ProviderType(value)
            except ValueError as exc:
                raise ProviderException(f"Unknown route provider: {value}.") from exc
        raise ProviderException("Route request does not specify a provider.")


__all__ = ["ProviderRouter"]
