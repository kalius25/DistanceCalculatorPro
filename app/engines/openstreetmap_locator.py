"""Centralized OpenStreetMap result locators."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

_DISTANCE = "#directions_route_distance"
_DURATION = "#directions_route_time"


class OpenStreetMapLocator:
    """OpenStreetMap locator contract isolated from parsing logic."""

    @staticmethod
    def route_distance(page: Page) -> Locator:
        """Return the stable total-distance output."""
        return page.locator(_DISTANCE)

    @staticmethod
    def route_duration(page: Page) -> Locator:
        """Return the stable total-duration output."""
        return page.locator(_DURATION)


__all__ = ["OpenStreetMapLocator"]
