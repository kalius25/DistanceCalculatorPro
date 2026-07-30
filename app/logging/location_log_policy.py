"""
Location logging policy.
"""

from __future__ import annotations

from app.config import (
    APP_MODE,
    AppMode,
)
from app.logging.sensitive_data import (
    SensitiveDataSanitizer,
)


class LocationLogPolicy:
    """Create safe metadata for route locations."""

    @staticmethod
    def build(
        *,
        origin: str,
        destination: str,
    ) -> dict[str, object]:
        """Return environment-appropriate location metadata."""

        if APP_MODE is AppMode.DEVELOPMENT:
            return {
                "origin": (SensitiveDataSanitizer.sanitize(origin)),
                "destination": (SensitiveDataSanitizer.sanitize(destination)),
            }

        return {
            "origin_present": bool(
                origin.strip(),
            ),
            "destination_present": bool(
                destination.strip(),
            ),
            "origin_length": len(
                origin.strip(),
            ),
            "destination_length": len(
                destination.strip(),
            ),
            "origin_hash": (SensitiveDataSanitizer.fingerprint(origin)),
            "destination_hash": (SensitiveDataSanitizer.fingerprint(destination)),
        }


__all__ = [
    "LocationLogPolicy",
]
