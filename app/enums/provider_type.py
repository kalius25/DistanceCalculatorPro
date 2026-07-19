"""
Supported route providers.
"""

from enum import StrEnum


class ProviderType(StrEnum):
    """
    Available routing providers.
    """

    GOOGLE_MAPS_WEB = "Google Maps Web"