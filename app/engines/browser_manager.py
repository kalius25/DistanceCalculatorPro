"""
Distance Calculator Pro.

Playwright browser lifecycle management.
"""

from __future__ import annotations

from types import TracebackType

from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    ViewportSize,
    sync_playwright,
)

from app.configuration.models import BrowserConfig
from app.exceptions.engine_exception import EngineException


class BrowserManager:
    """Manage the Playwright browser lifecycle."""

    def __init__(
        self,
        config: BrowserConfig,
    ) -> None:
        """
        Initialize the browser manager.

        Parameters
        ----------
        config:
            Browser-specific immutable configuration.
        """
        self._config = config

        self._playwright: Playwright | None = None
        self._browser: Browser | None = None
        self._context: BrowserContext | None = None

    def start(self) -> None:
        if self._browser is not None:
            return

        self._playwright = sync_playwright().start()

        self._browser = self._playwright.chromium.launch(
            headless=self._config.headless,
            slow_mo=self._config.slow_mo,
        )

        viewport: ViewportSize = {
            "width": self._config.viewport_width,
            "height": self._config.viewport_height,
        }

        if self._config.user_agent is None:
            self._context = self._browser.new_context(
                locale=self._config.locale,
                viewport=viewport,
            )
        else:
            self._context = self._browser.new_context(
                locale=self._config.locale,
                viewport=viewport,
                user_agent=self._config.user_agent,
            )

        self._context.set_default_timeout(
            self._config.timeout,
        )

    def new_page(self) -> Page:
        """
        Create a new page in the managed browser context.

        Raises
        ------
        EngineException
            If the browser context has not been started.
        """
        if self._context is None:
            raise EngineException(
                "Browser chưa được khởi động."
            )

        return self._context.new_page()

    def close(self) -> None:
        """
        Close all managed Playwright resources.

        The method is safe to call repeatedly or when one or more
        resources have already been closed.
        """
        if self._context is not None:
            self._context.close()
            self._context = None

        if self._browser is not None:
            self._browser.close()
            self._browser = None

        if self._playwright is not None:
            self._playwright.stop()
            self._playwright = None

    def __enter__(self) -> BrowserManager:
        """Start the browser and return this manager."""
        self.start()

        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close managed resources when leaving the context."""
        self.close()
