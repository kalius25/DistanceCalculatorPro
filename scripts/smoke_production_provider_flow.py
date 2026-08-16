"""Smoke-test Bing/OSM through the production provider calculation flow."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from app.configuration.configuration_loader import ConfigurationLoader
from app.diagnostics import DiagnosticsManager
from app.engines.bing_maps_engine import BingMapsEngine
from app.engines.browser_manager import BrowserManager
from app.engines.openstreetmap_engine import OpenStreetMapEngine
from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest
from app.providers.bing_web_provider import BingWebProvider
from app.providers.openstreetmap_web_provider import (
    OpenStreetMapWebProvider,
)
from app.providers.provider_router import ProviderRouter
from app.services.calculation_service import CalculationService

_ORIGIN = "10.113922624804262,105.69436247381175"
_DESTINATION = "10.892645,105.041044"


@dataclass(slots=True)
class SmokeResult:
    provider: str
    travel_mode: str
    success: bool
    route_count: int
    selected_route: int | None
    distance_km: float | None
    duration_minutes: int | None
    duration_text: str | None
    error: str | None


def _create_service() -> CalculationService:
    configuration = ConfigurationLoader.load()
    diagnostics = DiagnosticsManager()
    browser = BrowserManager(configuration.browser)

    bing = BingWebProvider(
        browser,
        BingMapsEngine(configuration.browser.timeout, diagnostics),
        diagnostics=diagnostics,
    )
    osm = OpenStreetMapWebProvider(
        browser,
        OpenStreetMapEngine(configuration.browser.timeout, diagnostics),
        diagnostics=diagnostics,
    )

    router = ProviderRouter(
        {
            ProviderType.BING_MAPS_WEB: bing,
            ProviderType.OPENSTREETMAP_WEB: osm,
        }
    )
    return CalculationService(router)


def _run_one(
    service: CalculationService,
    provider: ProviderType,
    travel_mode: TravelMode,
) -> SmokeResult:
    request = RouteRequest(
        origin=_ORIGIN,
        destination=_DESTINATION,
        travel_mode=travel_mode,
        metadata={"provider": provider},
    )

    service.start_batch()
    try:
        result = service.calculate(request)
    finally:
        service.finish_batch()

    best = result.best_route
    return SmokeResult(
        provider=provider.value,
        travel_mode=travel_mode.value,
        success=result.success,
        route_count=len(result.routes),
        selected_route=(result.selected_route if result.routes else None),
        distance_km=best.distance_km if best is not None else None,
        duration_minutes=(best.duration_minutes if best is not None else None),
        duration_text=best.duration_text if best is not None else None,
        error=result.error or None,
    )


def _print_result(result: SmokeResult) -> None:
    print()
    print(f"== {result.provider} / {result.travel_mode} ==")
    print(f"Calculation: {'PASS' if result.success else 'FAIL'}")
    print(f"Routes parsed: {result.route_count}")
    if result.success:
        print(f"Selected route: {result.selected_route}")
        print(f"Distance: {result.distance_km} km")
        print(f"Duration: {result.duration_minutes} minutes")
        print(f"Duration text: {result.duration_text}")
    elif result.error:
        print(f"Error: {result.error}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Validate Bing Maps/OpenStreetMap through production "
            "CalculationService + ProviderRouter."
        )
    )
    parser.add_argument(
        "--provider",
        choices=("all", "bing", "osm"),
        default="all",
    )
    parser.add_argument(
        "--mode",
        choices=("driving", "walking"),
        default="driving",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/production-provider-smoke"),
    )
    args = parser.parse_args(argv)

    providers: list[ProviderType] = []
    if args.provider in ("all", "bing"):
        providers.append(ProviderType.BING_MAPS_WEB)
    if args.provider in ("all", "osm"):
        providers.append(ProviderType.OPENSTREETMAP_WEB)

    travel_mode = TravelMode(args.mode)
    service = _create_service()
    results = [_run_one(service, provider, travel_mode) for provider in providers]

    for result in results:
        _print_result(result)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    output_dir = args.output / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "report.json"
    report_path.write_text(
        json.dumps(
            [asdict(result) for result in results],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print()
    print(f"Report: {report_path}")
    return 0 if all(result.success for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
