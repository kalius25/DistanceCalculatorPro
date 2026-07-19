from enum import Enum


class RoutePreference(str, Enum):
    """
    Tùy chọn ưu tiên tuyến đường.
    """

    AUTO = "auto"

    AVOID = "avoid"