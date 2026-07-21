from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult


class BaseProvider(ABC):
    """Base class for all route providers."""

    @abstractmethod
    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:
        """Calculate routes for the given request."""
        raise NotImplementedError