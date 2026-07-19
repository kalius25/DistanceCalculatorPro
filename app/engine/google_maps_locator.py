"""
Distance Calculator Pro

Google Maps Locator

Tập trung toàn bộ locator của Google Maps vào một nơi.
Nếu Google thay đổi giao diện, chỉ cần sửa file này.
"""

from __future__ import annotations

from playwright.sync_api import Locator
from playwright.sync_api import Page


class GoogleMapsLocator:

    @staticmethod
    def search_box(page: Page) -> Locator:
        """
        Ô nhập địa điểm.
        """
        return page.locator('input[name="q"]')

    @staticmethod
    def search_button(page: Page) -> Locator:
        """
        Nút tìm kiếm.
        """
        return page.locator("#searchbox-searchbutton")

    @staticmethod
    def directions_button(page: Page) -> Locator:
        """
        Nút Chỉ đường.
        """
        return page.locator('button[data-value="Directions"]')

    @staticmethod
    def route_input(page: Page, index: int) -> Locator:
        """
        Ô nhập điểm đi / điểm đến.

        index = 0 -> Origin
        index = 1 -> Destination
        """
        return page.locator('input[aria-label]').nth(index)

    @staticmethod
    def transport_driving(page: Page) -> Locator:
        """
        Chế độ lái xe.
        """
        return page.locator('button[data-travel_mode="0"]')

    @staticmethod
    def route_panel(page: Page) -> Locator:
        """
        Khu vực hiển thị kết quả tuyến đường.
        """
        return page.locator('div[role="main"]')