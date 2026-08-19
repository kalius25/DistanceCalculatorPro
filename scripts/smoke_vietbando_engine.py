"""Live VietBanDo engine extraction smoke."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

from app.engines.browser_executable import resolve_browser_executable
from app.engines.vietbando_engine import VietBanDoEngine
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest

_ORIGIN = "10.113922624804262,105.69436247381175"
_DESTINATION = "10.892645,105.041044"


@dataclass(slots=True)
class LiveResult:
    mode: str
    success: bool
    route_count: int
    distance_text: str
    distance_km: float | None
    duration_available: bool
    error: str | None


def _request(mode: TravelMode) -> RouteRequest:
    return RouteRequest(
        origin=_ORIGIN,
        destination=_DESTINATION,
        travel_mode=mode,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate live VietBanDo engine extraction."
    )
    parser.add_argument(
        "--mode",
        choices=("all", "driving", "truck", "walking"),
        default="all",
    )
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/vietbando-engine-smoke"),
    )
    args = parser.parse_args(argv)

    mode_map = {
        "driving": TravelMode.DRIVING,
        "truck": TravelMode.TRUCK,
        "walking": TravelMode.WALKING,
    }
    modes = tuple(mode_map.values()) if args.mode == "all" else (mode_map[args.mode],)

    executable = resolve_browser_executable()
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        executable_path=str(executable),
        headless=args.headless,
    )
    results: list[LiveResult] = []

    try:
        context = browser.new_context(
            locale="vi-VN",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        engine = VietBanDoEngine(30_000)

        for mode in modes:
            error: str | None = None
            routes = []
            try:
                routes = engine.find_routes(page, _request(mode))
            except Exception as exc:
                error = f"{type(exc).__name__}: {exc}"

            route = routes[0] if routes else None
            result = LiveResult(
                mode=mode.value,
                success=route is not None,
                route_count=len(routes),
                distance_text=(route.distance_text if route is not None else ""),
                distance_km=(route.distance_km if route is not None else None),
                duration_available=bool(
                    route and route.raw.get("duration_available", True)
                ),
                error=error,
            )
            results.append(result)

            print()
            print(f"== VietBanDo / {mode.value} ==")
            print("Engine extraction: " f"{'PASS' if result.success else 'FAIL'}")
            print(f"Routes parsed: {result.route_count}")
            print(f"Distance: {result.distance_text}")
            print("Duration available: " f"{result.duration_available}")
            if result.error:
                print(f"Error: {result.error}")

        context.close()
    finally:
        browser.close()
        playwright.stop()

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
