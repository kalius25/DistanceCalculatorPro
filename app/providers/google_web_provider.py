"""
Distance Calculator Pro.

Google Maps web provider implementation.
"""

from __future__ import annotations

from app.engines.browser_manager import BrowserManager
from app.engines.google_maps_engine import GoogleMapsEngine
from app.exceptions import EngineException
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.providers.base_provider import BaseProvider


class GoogleWebProvider(BaseProvider):
    """
    Calculate routes through the Google Maps web interface.

    BrowserManager and GoogleMapsEngine are created externally and
    injected through the constructor.
    """

    PROVIDER_NAME = "google_web"

    def __init__(
        self,
        browser: BrowserManager,
        engine: GoogleMapsEngine,
    ) -> None:
        """
        Initialize the provider with its required dependencies.

        Parameters
        ----------
        browser:
            Browser lifecycle manager.
        engine:
            Google Maps route extraction engine.
        """
        self._browser = browser
        self._engine = engine

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:
        """
        Calculate routes for the supplied request.

        EngineException is converted into a failed RouteResult.
        Unexpected exceptions are intentionally allowed to propagate.
        """
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
