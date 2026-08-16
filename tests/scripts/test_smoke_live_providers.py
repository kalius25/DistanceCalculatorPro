from unittest.mock import MagicMock, patch

from scripts.smoke_live_providers import (
    _launch_browser,
    _probe_metric_elements,
)


def test_launch_browser_resolves_executable_before_starting_playwright() -> None:
    calls: list[str] = []
    playwright = MagicMock()
    manager = MagicMock()
    manager.start.return_value = playwright
    browser = MagicMock()
    playwright.chromium.launch.return_value = browser

    def resolve() -> str:
        calls.append("resolve")
        return "chromium.exe"

    def sync() -> MagicMock:
        calls.append("sync")
        return manager

    with (
        patch(
            "scripts.smoke_live_providers.resolve_browser_executable",
            side_effect=resolve,
        ),
        patch(
            "scripts.smoke_live_providers.sync_playwright",
            side_effect=sync,
        ),
    ):
        returned_playwright, returned_browser = _launch_browser(False)

    assert calls == ["resolve", "sync"]
    assert returned_playwright is playwright
    assert returned_browser is browser
    playwright.chromium.launch.assert_called_once_with(
        executable_path="chromium.exe",
        headless=False,
    )


def test_probe_metric_elements_maps_javascript_results() -> None:
    page = MagicMock()
    page.locator.return_value.evaluate_all.return_value = [
        {
            "tag": "div",
            "element_id": "route",
            "class_name": "summary",
            "role": "",
            "text": "10 km 20 min",
        }
    ]

    probes = _probe_metric_elements(page)

    assert len(probes) == 1
    assert probes[0].element_id == "route"
    assert probes[0].text == "10 km 20 min"


def test_probe_metric_elements_is_non_fatal() -> None:
    page = MagicMock()
    page.locator.return_value.evaluate_all.side_effect = RuntimeError(
        "javascript probe failed"
    )

    assert _probe_metric_elements(page) == []
