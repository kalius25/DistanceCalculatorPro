"""Bing Maps route-result parser."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

from app import config
from app.diagnostics import DiagnosticsManager
from app.engines.bing_maps_locator import BingMapsLocator
from app.logging import LoggingManager
from app.models.route_option import RouteOption
from app.parsers.route_text_parser import parse_route_text

logger = LoggingManager.get_logger(__name__)


def _parse_locator(locator: Locator) -> RouteOption | None:
    """Parse one visible route-result container."""
    return parse_route_text(
        locator.inner_text(),
        provider="bing_maps_web",
    )


class BingMapsParser:
    """Extract normalized RouteOption objects from Bing Maps."""

    @staticmethod
    def parse(
        page: Page,
        diagnostics: DiagnosticsManager | None = None,
    ) -> list[RouteOption]:
        """Parse available route results from the current page."""
        locator = BingMapsLocator.route_results(page)
        count = min(locator.count(), config.PARSER_MAX_ROUTES)
        routes: list[RouteOption] = []

        for index in range(count):
            option = _parse_locator(locator.nth(index))
            if option is not None:
                routes.append(option)

        if diagnostics is not None:
            diagnostics.log_routes(logger, routes)
        return routes


__all__ = ["BingMapsParser"]
