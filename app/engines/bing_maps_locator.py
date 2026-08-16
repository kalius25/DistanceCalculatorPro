"""Centralized Bing Maps result locators."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

_ROUTE_RESULTS = "[class*='routeResultListItemContainer_']"


class BingMapsLocator:
    """Bing Maps locator contract isolated from parsing logic."""

    @staticmethod
    def route_results(page: Page) -> Locator:
        """Return live Bing route-card containers."""
        return page.locator(_ROUTE_RESULTS)


__all__ = ["BingMapsLocator"]
