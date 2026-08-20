"""Google Maps route extraction through path-based navigation."""

from __future__ import annotations

from typing import Literal

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.configuration.models import GoogleMapsConfig
from app.diagnostics import DiagnosticsManager
from app.engines.base_engine import BaseEngine
from app.engines.google_maps_locator import GoogleMapsLocator
from app.engines.google_maps_url_builder import GoogleMapsUrlBuilder
from app.enums.travel_mode import TravelMode
from app.exceptions import EngineException, ErrorCode, ParserException
from app.logging import LoggingManager
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.parsers.google_maps_parser import GoogleMapsParser

_WAIT_STATE: Literal["visible"] = "visible"

logger = LoggingManager.get_logger(__name__)


class GoogleMapsEngine(BaseEngine):
    """Navigate directly to a Google Maps directions URL and parse routes."""

    def __init__(
        self,
        config: GoogleMapsConfig,
        locator: GoogleMapsLocator,
        parser: GoogleMapsParser,
        diagnostics: DiagnosticsManager | None = None,
    ) -> None:
        self._config = config
        self._locator = locator
        self._parser = parser
        self._diagnostics = diagnostics or DiagnosticsManager()

    def find_routes(
        self,
        page: Page,
        request: RouteRequest,
    ) -> list[RouteOption]:
        """Open a complete directions URL and return parsed route options."""
        self._validate_request(request)
        context = {
            "origin": request.origin,
            "destination": request.destination,
            "travel_mode": request.travel_mode.value,
            "timeout": request.timeout,
        }
        url = GoogleMapsUrlBuilder.build(request)

        try:
            self._diagnostics.trace_browser(
                logger,
                "GOOGLE_MAPS_NAVIGATION_STARTED",
                url=url,
            )
            page.goto(
                url,
                timeout=self._config.action_timeout,
                wait_until="domcontentloaded",
            )
            self._select_non_default_travel_mode(page, request)

            route_cards = self._locator.route_cards(page)
            route_cards.first.wait_for(
                state=_WAIT_STATE,
                timeout=request.timeout * 1000,
            )
            route_count = route_cards.count()
            self._diagnostics.trace_browser(
                logger,
                "GOOGLE_MAPS_ROUTE_CARDS_FOUND",
                route_card_count=route_count,
            )
            routes = self._parser.parse(page, self._diagnostics)
            self._diagnostics.capture_page(
                page,
                label="google_maps_success",
                payload={
                    "url": url,
                    "route_card_count": route_count,
                    "parsed_route_count": len(routes),
                    "routes": [
                        {
                            "summary": route.summary,
                            "distance_km": route.distance_km,
                            "duration_minutes": route.duration_minutes,
                            "has_toll": route.has_toll,
                            "has_ferry": route.has_ferry,
                            "has_highway": route.has_highway,
                        }
                        for route in routes
                    ],
                },
            )
            return routes

        except ParserException:
            self._capture_failure(page, url, "parser_error")
            raise
        except PlaywrightTimeoutError as exc:
            self._capture_failure(page, url, "timeout")
            raise EngineException(
                "Google Maps request timed out.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=exc,
                context={**context, "url": url},
            ) from exc
        except PlaywrightError as exc:
            self._capture_failure(page, url, "browser_error")
            raise EngineException(
                "Google Maps browser operation failed.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=exc,
                context={**context, "url": url},
            ) from exc

    def _capture_failure(
        self,
        page: Page,
        url: str,
        label: str,
    ) -> None:
        try:
            if not page.is_closed():
                self._diagnostics.capture_page(
                    page,
                    label=label,
                    payload={"url": url, "failure": label},
                )
        except PlaywrightError:
            return

    @staticmethod
    def _validate_request(request: RouteRequest) -> None:
        if not request.origin.strip():
            raise ValueError("Origin cannot be empty.")
        if not request.destination.strip():
            raise ValueError("Destination cannot be empty.")
        if request.timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

    def _select_non_default_travel_mode(
        self,
        page: Page,
        request: RouteRequest,
    ) -> None:
        """Accept modes already encoded by the Google Maps route URL."""
        if request.travel_mode in (
            TravelMode.DRIVING,
            TravelMode.WALKING,
        ):
            return
        raise NotImplementedError(f"Unsupported travel mode: {request.travel_mode}")


__all__ = ["GoogleMapsEngine"]
