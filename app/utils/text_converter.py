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


def _normalize_number(value: str) -> float:
    """
    Convert a numeric string to float.

    Supports both decimal separators:
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

        Supported formats:
            350 m
            999 m
            1 km
            1.2 km
            1,2 km
            15 mi
            500 ft

        Returns:
            Distance in kilometer, or None if invalid.
        """

        if not text:
            return None

        match = _DISTANCE_PATTERN.fullmatch(text.strip())

        if not match:
            return None

        value = _normalize_number(match.group(1))
        unit = match.group(2).lower()

        if unit == "km":
            return value

        if unit == "m":
            return value / 1000

        if unit == "mi":
            return value * 1.609344

        if unit == "ft":
            return value * 0.3048 / 1000

        return None

    @staticmethod
    def duration_to_minutes(text: str | None) -> int | None:
        """
        Convert duration text to total minutes.

        Supported Vietnamese:
            45 phút
            45 p
            1 giờ
            1 giờ 15 phút
            2 giờ 5 p

        Supported English:
            45 min
            1 hr
            1 hour
            2 hr 30 min

        Returns:
            Total minutes, or None if invalid.
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
