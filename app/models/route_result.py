from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.exceptions import ErrorCode

from .route_option import RouteOption
from .route_request import RouteRequest


@dataclass(slots=True)
class RouteResult:
    """
    Represents the result of a route calculation.
    """

    success: bool

    request: RouteRequest

    provider: str

    routes: list[RouteOption] = field(default_factory=list)

    selected_route: int = 0

    error: str = ""

    error_code: ErrorCode | None = None

    context: dict[str, Any] = field(default_factory=dict)

    @property
    def best_route(self) -> RouteOption | None:
        """
        Returns the currently selected route.

        Returns
        -------
        RouteOption | None
            Selected route if available; otherwise None.
        """
        if not self.routes:
            return None

        if self.selected_route < 0:
            return None

        if self.selected_route >= len(self.routes):
            return None

        return self.routes[self.selected_route]