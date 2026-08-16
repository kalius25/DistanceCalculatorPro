"""Live browser validation for Bing Maps and OpenStreetMap providers."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from playwright.sync_api import Browser, Page, sync_playwright

from app.engines.bing_maps_engine import BingMapsEngine
from app.engines.bing_maps_url_builder import BingMapsUrlBuilder
from app.engines.browser_executable import resolve_browser_executable
from app.engines.openstreetmap_engine import OpenStreetMapEngine
from app.engines.openstreetmap_url_builder import OpenStreetMapUrlBuilder
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest
from app.parsers.route_text_parser import parse_route_text

_ORIGIN = "10.113922624804262,105.69436247381175"
_DESTINATION = "10.892645,105.041044"

_BING_CANDIDATES = (
    "[class*='routeResultListItemContainer_']",
    "[class*='routeResultListItem_']",
    "[class*='routeInfo_']",
    "[id^='routeDistance_']",
)

_OSM_CANDIDATES = (
    "#directions_route_distance",
    "#directions_route_time",
    "#sidebar_content",
)

ProviderRunner = Callable[[Page, RouteRequest], list[object]]
UrlBuilder = Callable[[RouteRequest], str]


@dataclass(slots=True)
class CandidateResult:
    selector: str
    count: int
    parseable: int
    samples: list[str]


@dataclass(slots=True)
class DomProbe:
    tag: str
    element_id: str
    class_name: str
    role: str
    text: str


@dataclass(slots=True)
class ProviderReport:
    provider: str
    url: str
    navigation_ok: bool
    engine_ok: bool
    engine_error: str | None
    route_count: int
    candidates: list[CandidateResult]
    dom_probes: list[DomProbe]
    interesting_lines: list[str]
    body_excerpt: str
    html_path: str | None
    screenshot: str | None


def _request(mode: TravelMode) -> RouteRequest:
    return RouteRequest(
        origin=_ORIGIN,
        destination=_DESTINATION,
        travel_mode=mode,
    )


def _candidate_results(
    page: Page,
    selectors: tuple[str, ...],
    provider_key: str,
) -> list[CandidateResult]:
    results: list[CandidateResult] = []

    for selector in selectors:
        locator = page.locator(selector)
        count = locator.count()
        parseable = 0
        samples: list[str] = []

        for index in range(min(count, 3)):
            text = locator.nth(index).inner_text().strip()
            if text and len(samples) < 2:
                samples.append(text[:800])
            if parse_route_text(text, provider=provider_key) is not None:
                parseable += 1

        results.append(
            CandidateResult(
                selector=selector,
                count=count,
                parseable=parseable,
                samples=samples,
            )
        )

    return results


def _probe_metric_elements(page: Page) -> list[DomProbe]:
    """Find small DOM elements that look like route metric containers."""
    try:
        raw = page.locator("body *").evaluate_all("""
        (elements) => {
          const metric = new RegExp(
            [
              "distance",
              "time",
              "km\\\\b",
              "mi\\\\b",
              "ft\\\\b",
              "minutes?\\\\b",
              "mins?\\\\b",
              "hours?\\\\b",
              "hrs?\\\\b",
              "phút",
              "giờ",
              "quãng đường",
              "thời gian"
            ].join("|"),
            "i"
          );
          const seen = new Set();
          const out = [];

          for (const el of elements) {
            const text = (el.innerText || "").trim();
            if (!text || text.length > 600 || !metric.test(text)) {
              continue;
            }

            const key = [
              el.tagName,
              el.id || "",
              typeof el.className === "string" ? el.className : "",
              el.getAttribute("role") || "",
              text
            ].join("|");

            if (seen.has(key)) {
              continue;
            }
            seen.add(key);

            out.push({
              tag: el.tagName.toLowerCase(),
              element_id: el.id || "",
              class_name:
                typeof el.className === "string" ? el.className : "",
              role: el.getAttribute("role") || "",
              text: text.slice(0, 600)
            });

            if (out.length >= 80) {
              break;
            }
          }
          return out;
        }
            """)
    except Exception:
        return []
    return [DomProbe(**item) for item in raw]


def _interesting_body_lines(body_text: str) -> list[str]:
    """Return body lines likely related to route distance or duration."""
    keywords = (
        "distance",
        "time",
        "km",
        "mile",
        "min",
        "hour",
        "quãng đường",
        "thời gian",
        "phút",
        "giờ",
    )
    output: list[str] = []

    for raw_line in body_text.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        if line and any(keyword in lower for keyword in keywords):
            output.append(line[:800])
        if len(output) >= 40:
            break

    return output


def _write_html(
    page: Page,
    artifact_dir: Path,
    provider_key: str,
) -> str | None:
    """Persist rendered HTML for selector analysis."""
    html_path = artifact_dir / f"{provider_key}.html"
    try:
        html_path.write_text(page.content(), encoding="utf-8")
        return str(html_path)
    except Exception:
        return None


def _validate_provider(
    *,
    page: Page,
    provider_name: str,
    provider_key: str,
    request: RouteRequest,
    build_url: UrlBuilder,
    run_engine: ProviderRunner,
    selectors: tuple[str, ...],
    artifact_dir: Path,
) -> ProviderReport:
    url = build_url(request)
    navigation_ok = False
    engine_ok = False
    engine_error: str | None = None
    route_count = 0

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30_000,
        )
        navigation_ok = True
        page.wait_for_timeout(8_000)
    except Exception as error:
        engine_error = f"navigation: {type(error).__name__}: {error}"

    if navigation_ok:
        try:
            routes = run_engine(page, request)
            route_count = len(routes)
            engine_ok = route_count > 0
        except Exception as error:
            engine_error = f"{type(error).__name__}: {error}"

    candidates = _candidate_results(page, selectors, provider_key)
    body_excerpt = ""
    try:
        body_excerpt = page.locator("body").inner_text()[:12_000]
    except Exception:
        body_excerpt = ""

    artifact_dir.mkdir(parents=True, exist_ok=True)
    dom_probes = _probe_metric_elements(page)
    interesting_lines = _interesting_body_lines(body_excerpt)
    html_path = _write_html(page, artifact_dir, provider_key)
    screenshot_path = artifact_dir / f"{provider_key}.png"
    screenshot: str | None = None
    try:
        page.screenshot(path=str(screenshot_path), full_page=True)
        screenshot = str(screenshot_path)
    except Exception:
        screenshot = None

    return ProviderReport(
        provider=provider_name,
        url=url,
        navigation_ok=navigation_ok,
        engine_ok=engine_ok,
        engine_error=engine_error,
        route_count=route_count,
        candidates=candidates,
        dom_probes=dom_probes,
        interesting_lines=interesting_lines,
        body_excerpt=body_excerpt,
        html_path=html_path,
        screenshot=screenshot,
    )


def _print_report(report: ProviderReport) -> None:
    print()
    print(f"== {report.provider} ==")
    print(f"URL: {report.url}")
    print(f"Navigation: {'PASS' if report.navigation_ok else 'FAIL'}")
    print(f"Engine extraction: {'PASS' if report.engine_ok else 'FAIL'}")
    print(f"Routes parsed: {report.route_count}")
    if report.engine_error:
        print(f"Error: {report.engine_error}")

    print("Candidate selectors:")
    for candidate in report.candidates:
        print(
            f"  {candidate.selector}: count={candidate.count}, "
            f"parseable={candidate.parseable}"
        )

    print("Interesting body lines:")
    if report.interesting_lines:
        for line in report.interesting_lines:
            print(f"  {line}")
    else:
        print("  <none>")

    print("DOM metric probes:")
    if report.dom_probes:
        for probe in report.dom_probes[:30]:
            identity = probe.tag
            if probe.element_id:
                identity += f"#{probe.element_id}"
            if probe.class_name:
                identity += f".{probe.class_name}"
            if probe.role:
                identity += f"[role={probe.role}]"
            print(f"  {identity}: {probe.text[:240]}")
    else:
        print("  <none>")

    if report.html_path:
        print(f"Rendered HTML: {report.html_path}")


def _launch_browser(headless: bool) -> tuple[object, Browser]:
    executable = resolve_browser_executable()
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        executable_path=str(executable),
        headless=headless,
    )
    return playwright, browser


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate live Bing Maps/OpenStreetMap extraction."
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
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/live-provider-validation"),
    )
    args = parser.parse_args(argv)

    mode = TravelMode(args.mode)
    request = _request(mode)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    artifact_dir = args.output / timestamp
    reports: list[ProviderReport] = []

    playwright, browser = _launch_browser(args.headless)
    try:
        context = browser.new_context(
            locale="vi-VN",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        if args.provider in ("all", "bing"):
            bing_engine = BingMapsEngine(30_000)
            reports.append(
                _validate_provider(
                    page=page,
                    provider_name="Bing Maps",
                    provider_key="bing_maps_web",
                    request=request,
                    build_url=BingMapsUrlBuilder.build,
                    run_engine=bing_engine.find_routes,
                    selectors=_BING_CANDIDATES,
                    artifact_dir=artifact_dir,
                )
            )

        if args.provider in ("all", "osm"):
            osm_engine = OpenStreetMapEngine(30_000)
            reports.append(
                _validate_provider(
                    page=page,
                    provider_name="OpenStreetMap",
                    provider_key="openstreetmap_web",
                    request=request,
                    build_url=OpenStreetMapUrlBuilder.build,
                    run_engine=osm_engine.find_routes,
                    selectors=_OSM_CANDIDATES,
                    artifact_dir=artifact_dir,
                )
            )

        context.close()
    finally:
        browser.close()
        playwright.stop()

    for report in reports:
        _print_report(report)

    artifact_dir.mkdir(parents=True, exist_ok=True)
    report_path = artifact_dir / "report.json"
    report_path.write_text(
        json.dumps(
            [asdict(report) for report in reports],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print()
    print(f"Report: {report_path}")

    return 0 if all(report.engine_ok for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
