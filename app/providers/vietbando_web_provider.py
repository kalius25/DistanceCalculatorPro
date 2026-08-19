"""VietBanDo production web provider."""

from __future__ import annotations

from app.providers.google_web_provider import GoogleWebProvider


class VietBanDoWebProvider(GoogleWebProvider):
    """VietBanDo provider using the shared browser lifecycle."""

    PROVIDER_NAME = "vietbando_web"


__all__ = ["VietBanDoWebProvider"]
