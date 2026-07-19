from app.engine.google_maps_engine import GoogleMapsEngine
from app.engine.google_maps_parser import GoogleMapsParser

from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult

from app.providers.base_provider import BaseProvider


class GoogleWebProvider(BaseProvider):

    def __init__(self, browser):

        self.engine = GoogleMapsEngine(browser)

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:

        page = self.engine.open_route(
            request.origin,
            request.destination,
        )

        page.wait_for_timeout(3000)

        return GoogleMapsParser.parse(
            page,
            request,
        )