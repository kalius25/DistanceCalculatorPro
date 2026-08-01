from __future__ import annotations

from abc import ABC, abstractmethod

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult


class BaseProvider(ABC):
    """Base class for all route providers."""

    def start_batch(self) -> None:
        """Allocate provider resources for one batch."""

    def finish_batch(self) -> None:
        """Release provider resources after one batch."""

    @abstractmethod
    def calculate(self, request: RouteRequest) -> RouteResult:
        """Calculate routes for the given request."""
        raise NotImplementedError
