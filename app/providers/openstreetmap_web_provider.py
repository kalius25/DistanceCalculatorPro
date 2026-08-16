"""OpenStreetMap production web provider."""

from __future__ import annotations

from app.providers.google_web_provider import GoogleWebProvider


class OpenStreetMapWebProvider(GoogleWebProvider):
    """OpenStreetMap provider using the shared browser lifecycle."""

    PROVIDER_NAME = "openstreetmap_web"


__all__ = ["OpenStreetMapWebProvider"]
