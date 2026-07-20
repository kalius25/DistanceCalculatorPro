from app.engines.google_maps_engine import GoogleMapsEngine
from app.parsers.google_maps_parser import GoogleMapsParser

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult

from app.providers.base_provider import BaseProvider


class GoogleWebProvider(BaseProvider):
    """Google Maps implementation of BaseProvider."""

    def __init__(self, browser) -> None:
        self._engine = GoogleMapsEngine(browser)

def calculate(
    self,
    request: RouteRequest,
) -> RouteResult:
    """
    Calculate routes using Google Maps.
    """

    try:
        page = self._engine.open_route(
            request.origin,
            request.destination,
        )

        routes = GoogleMapsParser.parse(page)

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