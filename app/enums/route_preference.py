"""
Route preference definitions.
"""

from enum import StrEnum


class RoutePreference(StrEnum):
    """
    Route preference.

    AUTO
        Use Google's default behavior.

    AVOID
        Try to avoid this road type.
    """

    AUTO = "auto"

    AVOID = "avoid"
