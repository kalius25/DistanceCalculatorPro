"""
Google Maps Engine.

This module is responsible for driving Google Maps through Playwright.

Responsibilities
----------------
- Open Google Maps Directions.
- Fill origin and destination.
- Select travel mode.
- Wait until route results are available.
- Delegate parsing to GoogleMapsParser.

This module must NOT:
- Parse HTML.
- Build business results.
- Retry failed requests.
- Perform business rule validation.
"""

from __future__ import annotations

from playwright.sync_api import Page
from collections.abc import Callable
from playwright.sync_api import Locator

from app import config
from app.engine.google_maps_locator import GoogleMapsLocator
from app.enums.travel_mode import TravelMode
from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.parser.google_maps_parser import GoogleMapsParser

_WAIT_STATE = "visible"

class GoogleMapsEngine:
    """
    Execute Google Maps routing workflow using Playwright.
    """

    _TRAVEL_MODE_LOCATORS: dict[
        TravelMode,
        Callable[[Page], Locator],
    ] = {
        TravelMode.DRIVING: GoogleMapsLocator.transport_driving,
    }

    def find_routes(
        self,
        page: Page,
        request: RouteRequest,
    ) -> list[RouteOption]:
        """
        Find available routes on Google Maps.

        Parameters
        ----------
        page:
            Active Playwright page.

        request:
            Route request.

        Returns
        -------
        list[RouteOption]
            Parsed route options.

        Raises
        ------
        ValueError
            If origin or destination is empty.

        NotImplementedError
            If travel mode is unsupported.
        """

        self._validate_request(request)

        page.goto(
            config.GOOGLE_MAPS_URL,
            timeout=config.BROWSER_TIMEOUT,
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

        route_panel = GoogleMapsLocator.route_panel(page)

        route_panel.wait_for(
            state=_WAIT_STATE,
            timeout=request.timeout * 1000,
        )

        return GoogleMapsParser.parse(page)

    @staticmethod
    def _validate_request(
        request: RouteRequest,
    ) -> None:
        """
        Validate route request.
        """

        if not request.origin.strip():
            raise ValueError("Origin cannot be empty.")

        if not request.destination.strip():
            raise ValueError("Destination cannot be empty.")

        if request.timeout <= 0:
            raise ValueError("Timeout must be greater than zero.")


    @staticmethod
    def _fill_route_input(
        page: Page,
        *,
        index: int,
        value: str,
    ) -> None:
        """
        Fill one route input.
        """

        locator = GoogleMapsLocator.route_input(
            page,
            index,
        )

        locator.wait_for(
            state=_WAIT_STATE,
            timeout=config.BROWSER_TIMEOUT,
        )

        locator.fill(value)

    def _select_travel_mode(
        self,
        page: Page,
        request: RouteRequest,
    ) -> None:
        """
        Select travel mode.
        """

        locator_factory = self._TRAVEL_MODE_LOCATORS.get(
            request.travel_mode,
        )

        if locator_factory is None:
            raise NotImplementedError(
                f"Unsupported travel mode: {request.travel_mode}"
            )

        locator_factory(page).click(
            timeout=config.BROWSER_TIMEOUT,
        )

__all__ = [
    "GoogleMapsEngine",
]