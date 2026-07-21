from dataclasses import dataclass, field

from app.enums.route_preference import RoutePreference
from app.enums.travel_mode import TravelMode


@dataclass(slots=True)
class RouteRequest:
    origin: str

    destination: str

    travel_mode: TravelMode = TravelMode.DRIVING

    alternatives: bool = True

    toll_preference: RoutePreference = RoutePreference.AUTO

    ferry_preference: RoutePreference = RoutePreference.AUTO

    highway_preference: RoutePreference = RoutePreference.AUTO

    language: str = "vi"

    region: str = "VN"

    timeout: int = 30

    metadata: dict = field(default_factory=dict)
