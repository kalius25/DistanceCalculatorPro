"""
Google Maps engine configuration model.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GoogleMapsConfig:
    """
    Immutable configuration used by GoogleMapsEngine.

    All timeout values are expressed in milliseconds.
    """

    base_url: str
    action_timeout: int