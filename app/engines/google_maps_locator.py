"""
Distance Calculator Pro

Google Maps Locator

Tập trung toàn bộ locator của Google Maps vào một nơi.
Nếu Google thay đổi giao diện, chỉ cần sửa file này.
"""

from __future__ import annotations

from playwright.sync_api import Locator, Page

# =============================================================================
# Internal Selectors
# =============================================================================

_SEARCH_BOX = 'input[name="q"]'

_SEARCH_BUTTON = "#searchbox-searchbutton"

_DIRECTIONS_BUTTON = 'button[data-value="Directions"]'

_ROUTE_INPUT = "input[aria-label]"

_TRANSPORT_DRIVING = 'button[data-travel_mode="0"]'

_ROUTE_PANEL = 'div[role="main"]'

_ROUTE_CARDS = "div.XdKEzd"


class GoogleMapsLocator:
    """Google Maps page locators."""

    @staticmethod
    def search_box(page: Page) -> Locator:
        """
        Ô nhập địa điểm.
        """
        return page.locator(_SEARCH_BOX)

    @staticmethod
    def search_button(page: Page) -> Locator:
        """
        Nút tìm kiếm.
        """
        return page.locator(_SEARCH_BUTTON)

    @staticmethod
    def directions_button(page: Page) -> Locator:
        """
        Nút Chỉ đường.
        """
        return page.locator(_DIRECTIONS_BUTTON)

    @staticmethod
    def route_input(page: Page, index: int) -> Locator:
        """
        Ô nhập điểm đi / điểm đến.

        index = 0 -> Origin
        index = 1 -> Destination
        """
        return page.locator(_ROUTE_INPUT).nth(index)

    @staticmethod
    def transport_driving(page: Page) -> Locator:
        """
        Chế độ lái xe.
        """
        return page.locator(_TRANSPORT_DRIVING)

    @staticmethod
    def route_panel(page: Page) -> Locator:
        """
        Khu vực hiển thị kết quả tuyến đường.
        """
        return page.locator(_ROUTE_PANEL)

    @staticmethod
    def route_cards(page: Page) -> Locator:
        """
        Danh sách các tuyến đường được Google Maps đề xuất.
        """
        return page.locator(_ROUTE_CARDS)
