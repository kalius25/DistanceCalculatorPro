from dataclasses import dataclass

from app.enums.provider_type import ProviderType


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    retry_count: int
    retry_delay: float
    default_provider: ProviderType
