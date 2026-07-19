"""
Distance Calculator Pro

Browser Manager
Quản lý Playwright Browser.
"""

from __future__ import annotations

from playwright.sync_api import Browser
from playwright.sync_api import BrowserContext
from playwright.sync_api import Page
from playwright.sync_api import Playwright
from playwright.sync_api import sync_playwright


class BrowserManager:
    """
    Quản lý vòng đời của Playwright.
    """

    def __init__(
        self,
        headless: bool = False,
    ) -> None:

        self._headless = headless

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    # =====================================================
    # Start
    # =====================================================

    def start(self) -> None:

        if self._browser is not None:
            return

        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            headless=self._headless
        )

        self._context = self._browser.new_context(
            locale="vi-VN"
        )

    # =====================================================
    # Page
    # =====================================================

    def new_page(self) -> Page:

        if self._context is None:
            raise RuntimeError(
                "Browser chưa được khởi động."
            )

        return self._context.new_page()

    # =====================================================
    # Close
    # =====================================================

    def close(self) -> None:

        if self._context is not None:
            self._context.close()
            self._context = None

        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    # =====================================================
    # Context Manager
    # =====================================================

    def __enter__(self):

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ):

        self.close()