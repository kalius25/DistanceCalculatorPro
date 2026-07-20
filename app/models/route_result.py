from dataclasses import dataclass, field

from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest


@dataclass(slots=True)
class RouteResult:
    success: bool

    request: RouteRequest

    provider: str

    routes: list[RouteOption] = field(default_factory=list)

    selected_route: int = 0

    error: str = ""

    @property
    def best_route(self):

        if not self.routes:
            return None

        return self.routes[self.selected_route]
