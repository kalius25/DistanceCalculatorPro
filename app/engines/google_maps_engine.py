"""
Google Maps Engine.

This module drives Google Maps through Playwright.

Responsibilities
----------------
- Open Google Maps Directions.
- Fill origin and destination.
- Select travel mode.
- Wait until route results are available.
- Delegate parsing to GoogleMapsParser.

This module must not:
- Read global application configuration.
- Parse route HTML directly.
- Build provider results.
- Manage browser lifecycle.
- Retry failed requests.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import Locator, Page
from playwright.sync_api import (
    TimeoutError as PlaywrightTimeoutError,
)

from app.configuration.models import GoogleMapsConfig
from app.engines.base_engine import BaseEngine
from app.engines.google_maps_locator import GoogleMapsLocator
from app.enums.travel_mode import TravelMode
from app.exceptions import (
    EngineException,
    ErrorCode,
    ParserException,
)
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.parsers.google_maps_parser import GoogleMapsParser

_WAIT_STATE: Literal["visible"] = "visible"


class GoogleMapsEngine(BaseEngine):
    """
    Execute the Google Maps routing workflow using Playwright.
    """

    def __init__(
        self,
        config: GoogleMapsConfig,
        locator: GoogleMapsLocator,
        parser: GoogleMapsParser,
    ) -> None:
        """
        Initialize the engine with required dependencies.

        Parameters
        ----------
        config:
            Google Maps engine-specific configuration.
        locator:
            Google Maps locator provider.
        parser:
            Google Maps route parser.
        """
        self._config = config
        self._locator = locator
        self._parser = parser

        self._travel_mode_locators: dict[
            TravelMode,
            Callable[[Page], Locator],
        ] = {
            TravelMode.DRIVING: (self._locator.transport_driving),
        }

    def find_routes(
        self,
        page: Page,
        request: RouteRequest,
    ) -> list[RouteOption]:
        """
        Find available routes on Google Maps.
        """
        self._validate_request(request)

        context = {
            "origin": request.origin,
            "destination": request.destination,
            "travel_mode": request.travel_mode.value,
            "timeout": request.timeout,
        }

        try:
            page.goto(
                self._config.base_url,
                timeout=self._config.action_timeout,
            )

            self._fill_route_input(
                page=page,
                index=0,
                value=request.origin,
            )

            self._fill_route_input(
                page=page,
                index=1,
                value=request.destination,
            )

            self._select_travel_mode(
                page=page,
                request=request,
            )

            route_panel = self._locator.route_panel(page)

            route_panel.wait_for(
                state=_WAIT_STATE,
                timeout=request.timeout * 1000,
            )

            return self._parser.parse(page)

        except ParserException:
            raise

        except PlaywrightTimeoutError as exc:
            raise EngineException(
                "Google Maps request timed out.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=exc,
                context=context,
            ) from exc

        except PlaywrightError as exc:
            raise EngineException(
                "Google Maps browser operation failed.",
                error_code=ErrorCode.ENGINE_ERROR,
                cause=exc,
                context=context,
            ) from exc

    @staticmethod
    def _validate_request(
        request: RouteRequest,
    ) -> None:
        """Validate the route request."""
        if not request.origin.strip():
            raise ValueError("Origin cannot be empty.")

        if not request.destination.strip():
            raise ValueError("Destination cannot be empty.")

        if request.timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")

    def _fill_route_input(
        self,
        page: Page,
        *,
        index: int,
        value: str,
    ) -> None:
        """Fill one route input."""
        locator = self._locator.route_input(
            page,
            index,
        )

        locator.wait_for(
            state=_WAIT_STATE,
            timeout=self._config.action_timeout,
        )

        locator.fill(value)

    def _select_travel_mode(
        self,
        page: Page,
        request: RouteRequest,
    ) -> None:
        """Select the requested travel mode."""
        locator_factory = self._travel_mode_locators.get(request.travel_mode)

        if locator_factory is None:
            raise NotImplementedError(
                "Unsupported travel mode: " f"{request.travel_mode}"
            )

        locator_factory(page).click(
            timeout=self._config.action_timeout,
        )


__all__ = [
    "GoogleMapsEngine",
]
