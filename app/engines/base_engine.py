from __future__ import annotations

from abc import ABC, abstractmethod

from playwright.sync_api import Page

from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest


class BaseEngine(ABC):
    """Base class for all routing engines."""

    @abstractmethod
    def find_routes(
        self,
        page: Page,
        request: RouteRequest,
    ) -> list[RouteOption]:
        """Find available routes."""
        raise NotImplementedError
