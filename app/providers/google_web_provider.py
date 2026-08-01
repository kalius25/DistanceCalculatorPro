"""Google Maps web provider implementation."""

from __future__ import annotations

from playwright.sync_api import Error as PlaywrightError

from app.engines.browser_manager import BrowserManager
from app.engines.google_maps_engine import GoogleMapsEngine
from app.exceptions import EngineException
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider


class GoogleWebProvider(BaseProvider):
    """Calculate a batch of routes with one shared browser lifecycle."""

    PROVIDER_NAME = "google_web"

    def __init__(
        self,
        browser: BrowserManager,
        engine: GoogleMapsEngine,
    ) -> None:
        self._browser = browser
        self._engine = engine
        self._batch_started = False

    def start_batch(self) -> None:
        if self._batch_started:
            return
        self._browser.start()
        self._batch_started = True

    def finish_batch(self) -> None:
        if not self._batch_started:
            return
        self._browser.close()
        self._batch_started = False

    def calculate(self, request: RouteRequest) -> RouteResult:
        """Calculate one route while reusing the batch browser context."""
        owns_browser = not self._batch_started
        if owns_browser:
            self.start_batch()

        page = None
        try:
            page = self._browser.new_page()
            routes = self._engine.find_routes(page, request)
            return RouteResult(
                success=True,
                request=request,
                provider=self.PROVIDER_NAME,
                routes=routes,
            )
        except EngineException as exc:
            return RouteResult(
                success=False,
                request=request,
                provider=self.PROVIDER_NAME,
                error=str(exc),
                error_code=exc.error_code,
                context=exc.context,
                exception=exc,
            )
        finally:
            if page is not None:
                try:
                    if not page.is_closed():
                        page.close()
                except PlaywrightError:
                    pass
            if owns_browser:
                self.finish_batch()
