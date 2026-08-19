"""Live DOM probe for VietBanDo route results."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Browser, Page, sync_playwright

from app.engines.browser_executable import resolve_browser_executable
from app.engines.vietbando_url_builder import VietBanDoUrlBuilder
from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest
from app.parsers.route_text_parser import parse_route_text

_ORIGIN = "10.113922624804262,105.69436247381175"
_DESTINATION = "10.892645,105.041044"

_CANDIDATE_SELECTORS = (
    "[class*='route']",
    "[id*='route']",
    "[class*='direction']",
    "[id*='direction']",
    "[class*='distance']",
    "[id*='distance']",
    "[class*='duration']",
    "[id*='duration']",
    "[class*='time']",
    "[id*='time']",
)


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
class VietBanDoReport:
    mode: str
    url: str
    navigation_ok: bool
    candidate_results: list[CandidateResult]
    dom_probes: list[DomProbe]
    interesting_lines: list[str]
    body_excerpt: str
    html_path: str | None
    screenshot_path: str | None
    error: str | None


def _request(mode: TravelMode) -> RouteRequest:
    return RouteRequest(
        origin=_ORIGIN,
        destination=_DESTINATION,
        travel_mode=mode,
    )


def _candidate_results(page: Page) -> list[CandidateResult]:
    results: list[CandidateResult] = []
    for selector in _CANDIDATE_SELECTORS:
        locator = page.locator(selector)
        count = locator.count()
        parseable = 0
        samples: list[str] = []

        for index in range(min(count, 5)):
            try:
                text = locator.nth(index).inner_text().strip()
            except Exception:
                continue
            if text and len(samples) < 3:
                samples.append(text[:1000])
            if (
                text
                and parse_route_text(
                    text,
                    provider="vietbando_web",
                )
                is not None
            ):
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
    try:
        raw = page.locator("body *").evaluate_all("""
            (elements) => {
              const metric = new RegExp(
                [
                  "distance",
                  "duration",
                  "time",
                  "route",
                  "km\\\\b",
                  "mi\\\\b",
                  "m\\\\b",
                  "minutes?\\\\b",
                  "mins?\\\\b",
                  "hours?\\\\b",
                  "hrs?\\\\b",
                  "phút",
                  "giờ",
                  "quãng đường",
                  "thời gian",
                  "khoảng cách"
                ].join("|"),
                "i"
              );
              const seen = new Set();
              const output = [];

              for (const element of elements) {
                const text = (element.innerText || "").trim();
                if (!text || text.length > 1000 || !metric.test(text)) {
                  continue;
                }

                const className =
                  typeof element.className === "string"
                    ? element.className
                    : "";
                const key = [
                  element.tagName,
                  element.id || "",
                  className,
                  element.getAttribute("role") || "",
                  text
                ].join("|");

                if (seen.has(key)) {
                  continue;
                }
                seen.add(key);

                output.push({
                  tag: element.tagName.toLowerCase(),
                  element_id: element.id || "",
                  class_name: className,
                  role: element.getAttribute("role") || "",
                  text: text.slice(0, 1000)
                });

                if (output.length >= 120) {
                  break;
                }
              }

              return output;
            }
            """)
    except Exception:
        return []

    return [DomProbe(**item) for item in raw]


def _interesting_lines(text: str) -> list[str]:
    keywords = (
        "km",
        "phút",
        "giờ",
        "minute",
        "hour",
        "distance",
        "duration",
        "time",
        "route",
        "quãng đường",
        "khoảng cách",
        "thời gian",
    )
    output: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        if line and any(keyword in lower for keyword in keywords):
            output.append(line[:1000])
        if len(output) >= 80:
            break
    return output


def _write_artifacts(
    page: Page,
    artifact_dir: Path,
    mode: TravelMode,
) -> tuple[str | None, str | None]:
    artifact_dir.mkdir(parents=True, exist_ok=True)

    html_path = artifact_dir / f"vietbando_{mode.value}.html"
    screenshot_path = artifact_dir / f"vietbando_{mode.value}.png"

    html: str | None
    screenshot: str | None

    try:
        html_path.write_text(page.content(), encoding="utf-8")
        html = str(html_path)
    except Exception:
        html = None

    try:
        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )
        screenshot = str(screenshot_path)
    except Exception:
        screenshot = None

    return html, screenshot


def _launch_browser(headless: bool) -> tuple[object, Browser]:
    executable = resolve_browser_executable()
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        executable_path=str(executable),
        headless=headless,
    )
    return playwright, browser


def _probe_mode(
    page: Page,
    mode: TravelMode,
    artifact_dir: Path,
    wait_ms: int,
) -> VietBanDoReport:
    request = _request(mode)
    url = VietBanDoUrlBuilder.build(request)
    navigation_ok = False
    error: str | None = None

    try:
        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30_000,
        )
        navigation_ok = True
        page.wait_for_timeout(wait_ms)
    except Exception as exc:
        error = f"{type(exc).__name__}: {exc}"

    body_excerpt = ""
    try:
        body_excerpt = page.locator("body").inner_text()[:20_000]
    except Exception:
        pass

    candidates = _candidate_results(page)
    probes = _probe_metric_elements(page)
    lines = _interesting_lines(body_excerpt)
    html, screenshot = _write_artifacts(
        page,
        artifact_dir,
        mode,
    )

    return VietBanDoReport(
        mode=mode.value,
        url=url,
        navigation_ok=navigation_ok,
        candidate_results=candidates,
        dom_probes=probes,
        interesting_lines=lines,
        body_excerpt=body_excerpt,
        html_path=html,
        screenshot_path=screenshot,
        error=error,
    )


def _print_report(report: VietBanDoReport) -> None:
    print()
    print(f"== VietBanDo / {report.mode} ==")
    print(f"URL: {report.url}")
    print("Navigation: " f"{'PASS' if report.navigation_ok else 'FAIL'}")
    if report.error:
        print(f"Error: {report.error}")

    print("Candidate selectors:")
    for candidate in report.candidate_results:
        print(
            f"  {candidate.selector}: "
            f"count={candidate.count}, "
            f"parseable={candidate.parseable}"
        )
        for sample in candidate.samples[:2]:
            print(f"    sample: {sample[:300]}")

    print("Interesting body lines:")
    if report.interesting_lines:
        for line in report.interesting_lines:
            print(f"  {line}")
    else:
        print("  <none>")

    print("DOM metric probes:")
    if report.dom_probes:
        for probe in report.dom_probes[:40]:
            identity = probe.tag
            if probe.element_id:
                identity += f"#{probe.element_id}"
            if probe.class_name:
                identity += f".{probe.class_name}"
            if probe.role:
                identity += f"[role={probe.role}]"
            print(f"  {identity}: {probe.text[:300]}")
    else:
        print("  <none>")

    if report.html_path:
        print(f"Rendered HTML: {report.html_path}")
    if report.screenshot_path:
        print(f"Screenshot: {report.screenshot_path}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Probe live VietBanDo route DOM.")
    parser.add_argument(
        "--mode",
        choices=("all", "driving", "truck", "walking"),
        default="all",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=10_000,
    )
    parser.add_argument("--headless", action="store_true")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("artifacts/vietbando-dom-probe"),
    )
    args = parser.parse_args(argv)

    if args.wait_ms < 0:
        parser.error("--wait-ms must be zero or greater")

    mode_map = {
        "driving": TravelMode.DRIVING,
        "truck": TravelMode.TRUCK,
        "walking": TravelMode.WALKING,
    }
    modes = tuple(mode_map.values()) if args.mode == "all" else (mode_map[args.mode],)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    artifact_dir = args.output / timestamp
    reports: list[VietBanDoReport] = []

    playwright, browser = _launch_browser(args.headless)
    try:
        context = browser.new_context(
            locale="vi-VN",
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()

        for mode in modes:
            reports.append(
                _probe_mode(
                    page,
                    mode,
                    artifact_dir,
                    args.wait_ms,
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
    return 0 if all(report.navigation_ok for report in reports) else 1


if __name__ == "__main__":
    raise SystemExit(main())
