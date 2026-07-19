from enum import Enum


class TravelMode(str, Enum):
    """
    Chế độ di chuyển.
    """

    DRIVING = "driving"
    WALKING = "walking"
    BICYCLING = "bicycling"
    TRANSIT = "transit"