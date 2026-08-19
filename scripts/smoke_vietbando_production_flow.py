"""Validate VietBanDo through the production provider/service flow."""

from __future__ import annotations

import argparse

from app.configuration.configuration_loader import ConfigurationLoader
from app.diagnostics import DiagnosticsManager
from app.engines.browser_manager import BrowserManager
from app.engines.vietbando_engine import VietBanDoEngine
from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest
from app.providers.provider_router import ProviderRouter
from app.providers.vietbando_web_provider import VietBanDoWebProvider
from app.services.calculation_service import CalculationService

_ORIGIN = "10.113922624804262,105.69436247381175"
_DESTINATION = "10.892645,105.041044"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate VietBanDo production calculation flow."
    )
    parser.add_argument(
        "--mode",
        choices=("driving", "truck", "walking"),
        default="driving",
    )
    args = parser.parse_args(argv)

    configuration = ConfigurationLoader.load()
    diagnostics = DiagnosticsManager()
    browser = BrowserManager(configuration.browser)
    provider = VietBanDoWebProvider(
        browser,
        VietBanDoEngine(configuration.browser.timeout, diagnostics),
        diagnostics=diagnostics,
    )
    service = CalculationService(ProviderRouter({ProviderType.VIETBANDO_WEB: provider}))
    request = RouteRequest(
        origin=_ORIGIN,
        destination=_DESTINATION,
        travel_mode=TravelMode(args.mode),
        metadata={"provider": ProviderType.VIETBANDO_WEB},
    )

    service.start_batch()
    try:
        result = service.calculate(request)
    finally:
        service.finish_batch()

    route = result.best_route
    print(f"Calculation: {'PASS' if result.success else 'FAIL'}")
    print(f"Routes parsed: {len(result.routes)}")
    if route is not None:
        print(f"Distance: {route.distance_km} km")
        print("Duration available: " f"{route.raw.get('duration_available', True)}")
    if result.error:
        print(f"Error: {result.error}")

    return 0 if result.success and route is not None else 1


if __name__ == "__main__":
    raise SystemExit(main())
