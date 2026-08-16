"""Bing Maps production web provider."""

from __future__ import annotations

from app.providers.google_web_provider import GoogleWebProvider


class BingWebProvider(GoogleWebProvider):
    """Bing Maps provider using the shared browser lifecycle."""

    PROVIDER_NAME = "bing_maps_web"


__all__ = ["BingWebProvider"]
