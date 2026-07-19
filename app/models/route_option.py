from dataclasses import dataclass, field


@dataclass(slots=True)
class RouteOption:

    summary: str = ""

    distance_text: str = ""

    distance_km: float = 0

    duration_text: str = ""

    duration_minutes: int = 0

    has_toll: bool = False

    has_ferry: bool = False

    has_highway: bool = False

    warnings: list[str] = field(default_factory=list)

    raw: dict = field(default_factory=dict)