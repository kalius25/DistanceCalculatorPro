"""
Travel mode definitions.
"""

from enum import StrEnum


class TravelMode(StrEnum):
    """
    Supported Google Maps travel modes.
    """

    DRIVING = "driving"
    WALKING = "walking"
    BICYCLING = "bicycling"
    TRANSIT = "transit"
