"""
Text conversion utilities.

This module converts text extracted from Google Maps into canonical values.

Canonical units:
    - Distance: kilometer (km)
    - Duration: minute

Design decisions:
    - Converter never raises exceptions for invalid input.
    - Invalid or unsupported values return None.
"""

from __future__ import annotations

import re

_DISTANCE_PATTERN = re.compile(
    r"^\s*(\d+(?:[.,]\d+)?)\s*(km|m|mi|ft)\s*$",
    re.IGNORECASE,
)

_HOUR_PATTERN = re.compile(
    r"(\d+)\s*(?:giờ|tiếng|h|hr|hrs|hour|hours)",
    re.IGNORECASE,
)

_MINUTE_PATTERN = re.compile(
    r"(\d+)\s*(?:phút|p|ph|min|mins|minute|minutes)",
    re.IGNORECASE,
)

_DISTANCE_FACTORS = {
    "km": 1.0,
    "m": 1 / 1000,
    "mi": 1.609344,
    "ft": 0.3048 / 1000,
}


def _normalize_number(value: str) -> float:
    """
    Convert a numeric string to float.

    Supports:
        1.5
        1,5
    """
    return float(value.replace(",", "."))


class TextConverter:
    """Utility class for converting text into canonical values."""

    @staticmethod
    def distance_to_km(text: str | None) -> float | None:
        """
        Convert a distance string to kilometer.

        Supported:
            350 m
            1 km
            1.2 km
            1,2 km
            15 mi
            500 ft
        """

        if not text:
            return None

        match = _DISTANCE_PATTERN.fullmatch(text.strip())

        if not match:
            return None

        value = _normalize_number(match.group(1))
        unit = match.group(2).lower()

        return value * _DISTANCE_FACTORS[unit]

    @staticmethod
    def duration_to_minutes(text: str | None) -> int | None:
        """
        Convert duration text to total minutes.
        """

        if not text:
            return None

        text = text.strip().lower()

        hour = 0
        minute = 0

        match = _HOUR_PATTERN.search(text)
        if match:
            hour = int(match.group(1))

        match = _MINUTE_PATTERN.search(text)
        if match:
            minute = int(match.group(1))

        total = hour * 60 + minute

        return total if total > 0 else None
