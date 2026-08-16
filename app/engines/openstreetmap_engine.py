"""OpenStreetMap web route extraction engine."""

from __future__ import annotations

from typing import Literal

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.diagnostics import DiagnosticsManager
from app.engines.base_engine import BaseEngine
from app.engines.openstreetmap_locator import OpenStreetMapLocator
from app.engines.openstreetmap_url_builder import OpenStreetMapUrlBuilder
from app.exceptions import EngineException, ErrorCode
from app.logging import LoggingManager
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.parsers.openstreetmap_parser import OpenStreetMapParser

_WAIT_UNTIL: Literal["domcontentloaded"] = "domcontentloaded"

logger = LoggingManager.get_logger(__name__)


class OpenStreetMapEngine(BaseEngine):
    """Navigate to OpenStreetMap and extract route options."""

    def __init__(
        self,
        action_timeout: int,
        diagnostics: DiagnosticsManager | None = None,
    ) -> None:
        if action_timeout <= 0:
            raise ValueError(
                "OpenStreetMap action timeout must be greater than zero."
            )
        self._action_timeout = action_timeout
        self._diagnostics = diagnostics or DiagnosticsManager()

    def navigate(
        self,
        page: Page,
        request: RouteRequest,
    ) -> str:
        """Navigate to the complete OpenStreetMap directions URL."""
        url = OpenStreetMapUrlBuilder.build(request)
        self._navigate(page, request, url)
        return url

    def find_routes(
        self,
        page: Page,
        request: RouteRequest,
    ) -> list[RouteOption]:
        """Navigate, wait for results, and parse route options."""
        url = OpenStreetMapUrlBuilder.build(request)
        self._navigate(page, request, url)

        try:
            distance = OpenStreetMapLocator.route_distance(page)
            distance.wait_for(
                state="visible",
                timeout=self._action_timeout,
            )
            routes = OpenStreetMapParser.parse(page, self._diagnostics)
            if not routes:
                raise EngineException(
                    "OpenStreetMap returned no parseable routes.",
                    error_code=ErrorCode.PARSER_ERROR,
                    context=self._context(request, url),
                )
            return routes
        except EngineException:
            raise
        except PlaywrightTimeoutError as error:
            raise EngineException(
                "OpenStreetMap route results timed out.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=error,
                context=self._context(request, url),
            ) from error
        except PlaywrightError as error:
            raise EngineException(
                "OpenStreetMap result extraction failed.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=error,
                context=self._context(request, url),
            ) from error

    def _navigate(
        self,
        page: Page,
        request: RouteRequest,
        url: str,
    ) -> None:
        context = self._context(request, url)
        try:
            self._diagnostics.trace_browser(
                logger,
                "OPENSTREETMAP_NAVIGATION_STARTED",
                url=url,
            )
            page.goto(
                url,
                timeout=self._action_timeout,
                wait_until=_WAIT_UNTIL,
            )
            self._diagnostics.trace_browser(
                logger,
                "OPENSTREETMAP_NAVIGATION_COMPLETED",
                url=url,
            )
        except PlaywrightTimeoutError as error:
            raise EngineException(
                "OpenStreetMap request timed out.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=error,
                context=context,
            ) from error
        except PlaywrightError as error:
            raise EngineException(
                "OpenStreetMap browser operation failed.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=error,
                context=context,
            ) from error

    @staticmethod
    def _context(
        request: RouteRequest,
        url: str,
    ) -> dict[str, str]:
        return {
            "origin": request.origin,
            "destination": request.destination,
            "travel_mode": request.travel_mode.value,
            "url": url,
        }


__all__ = ["OpenStreetMapEngine"]
