from __future__ import annotations

from app.engines.base_engine import BaseEngine
from app.engines.browser_manager import BrowserManager
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider


class GoogleWebProvider(BaseProvider):
    def __init__(
        self,
        browser: BrowserManager | None = None,
        engine: BaseEngine | None = None,
    ) -> None:
        self._browser = browser or BrowserManager()

        if engine is None:
            from app.engines.google_maps_engine import GoogleMapsEngine

            engine = GoogleMapsEngine()

        self._engine = engine

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:
        try:
            with self._browser as browser:
                page = browser.new_page()

                routes = self._engine.find_routes(
                    page,
                    request,
                )

            return RouteResult(
                success=True,
                request=request,
                provider="google_web",
                routes=routes,
            )

        except Exception as ex:
            return RouteResult(
                success=False,
                request=request,
                provider="google_web",
                error=str(ex),
            )