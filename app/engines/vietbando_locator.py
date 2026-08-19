"""Centralized VietBanDo result locators."""

from __future__ import annotations

from playwright.sync_api import Locator, Page

_TOTAL_DISTANCE = "#FindPathStatus"


class VietBanDoLocator:
    """VietBanDo locator contract isolated from parsing logic."""

    @staticmethod
    def route_distance(page: Page) -> Locator:
        """Return the stable total-route distance output."""
        return page.locator(_TOTAL_DISTANCE)


__all__ = ["VietBanDoLocator"]
