"""Bing Maps web navigation foundation."""

from __future__ import annotations

from typing import Literal

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Page
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from app.diagnostics import DiagnosticsManager
from app.engines.bing_maps_url_builder import BingMapsUrlBuilder
from app.exceptions import EngineException, ErrorCode
from app.logging import LoggingManager
from app.models.route_request import RouteRequest

_WAIT_UNTIL: Literal["domcontentloaded"] = "domcontentloaded"

logger = LoggingManager.get_logger(__name__)


class BingMapsEngine:
    """Navigate to Bing Maps directions while parser work remains isolated."""

    def __init__(
        self,
        action_timeout: int,
        diagnostics: DiagnosticsManager | None = None,
    ) -> None:
        if action_timeout <= 0:
            raise ValueError("Bing Maps action timeout must be greater than zero.")
        self._action_timeout = action_timeout
        self._diagnostics = diagnostics or DiagnosticsManager()

    def navigate(
        self,
        page: Page,
        request: RouteRequest,
    ) -> str:
        """Navigate to the complete Bing Maps directions URL."""
        url = BingMapsUrlBuilder.build(request)
        context = {
            "origin": request.origin,
            "destination": request.destination,
            "travel_mode": request.travel_mode.value,
            "url": url,
        }

        try:
            self._diagnostics.trace_browser(
                logger,
                "BING_MAPS_NAVIGATION_STARTED",
                url=url,
            )
            page.goto(
                url,
                timeout=self._action_timeout,
                wait_until=_WAIT_UNTIL,
            )
            self._diagnostics.trace_browser(
                logger,
                "BING_MAPS_NAVIGATION_COMPLETED",
                url=url,
            )
            return url
        except PlaywrightTimeoutError as error:
            raise EngineException(
                "Bing Maps request timed out.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=error,
                context=context,
            ) from error
        except PlaywrightError as error:
            raise EngineException(
                "Bing Maps browser operation failed.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=error,
                context=context,
            ) from error


__all__ = ["BingMapsEngine"]
