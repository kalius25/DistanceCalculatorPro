from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock

from app.diagnostics import DiagnosticsManager, DiagnosticsSettings
from app.models.route_option import RouteOption


def make_route() -> RouteOption:
    return RouteOption(
        summary="QL1A",
        distance_text="8.6 km",
        distance_km=8.6,
        duration_text="24 phút",
        duration_minutes=24,
        has_toll=False,
        has_ferry=False,
        has_highway=True,
    )


def test_diagnostics_are_disabled_by_default() -> None:
    manager = DiagnosticsManager()
    logger = MagicMock()
    page = MagicMock()

    manager.trace_browser(logger, "EVENT", value=1)
    manager.log_routes(logger, [make_route()])
    manager.capture_page(page, label="route")

    logger.debug.assert_not_called()
    page.content.assert_not_called()
    page.screenshot.assert_not_called()


def test_trace_and_parser_logging_are_emitted_when_enabled() -> None:
    manager = DiagnosticsManager(
        DiagnosticsSettings(
            enabled=True,
            trace_browser=True,
            parser_diagnostics=True,
        )
    )
    logger = MagicMock()

    manager.trace_browser(logger, "BROWSER_EVENT", value=1)
    manager.log_routes(logger, [make_route()])

    assert logger.debug.call_count == 2
    assert logger.debug.call_args_list[0].args == ("BROWSER_EVENT",)
    assert logger.debug.call_args_list[1].args == ("ROUTE_PARSED",)


def test_capture_page_writes_enabled_artifacts(tmp_path: Path) -> None:
    manager = DiagnosticsManager(
        DiagnosticsSettings(
            enabled=True,
            save_html=True,
            save_screenshot=True,
            save_json=True,
            output_directory=tmp_path,
        )
    )
    page = MagicMock()
    page.content.return_value = "<html>route</html>"

    manager.capture_page(page, label="route success", payload={"count": 4})

    html_files = list((tmp_path / "html").glob("*.html"))
    json_files = list((tmp_path / "json").glob("*.json"))
    assert html_files[0].read_text(encoding="utf-8") == "<html>route</html>"
    assert json.loads(json_files[0].read_text(encoding="utf-8")) == {"count": 4}
    page.screenshot.assert_called_once()


def test_update_replaces_runtime_settings() -> None:
    manager = DiagnosticsManager()
    settings = DiagnosticsSettings(enabled=True)

    manager.update(settings)

    assert manager.settings is settings


def test_capture_page_supports_each_artifact_independently(tmp_path: Path) -> None:
    page = MagicMock()
    page.content.return_value = "<html>diagnostic</html>"

    html_manager = DiagnosticsManager(
        DiagnosticsSettings(
            enabled=True,
            save_html=True,
            output_directory=tmp_path / "html_only",
        )
    )
    html_manager.capture_page(page, label="route")
    assert len(list((tmp_path / "html_only" / "html").glob("*.html"))) == 1

    screenshot_manager = DiagnosticsManager(
        DiagnosticsSettings(
            enabled=True,
            save_screenshot=True,
            output_directory=tmp_path / "screenshot_only",
        )
    )
    screenshot_manager.capture_page(page, label="route")

    json_manager = DiagnosticsManager(
        DiagnosticsSettings(
            enabled=True,
            save_json=True,
            output_directory=tmp_path / "json_only",
        )
    )
    json_manager.capture_page(page, label="route", payload=None)
    json_files = list((tmp_path / "json_only" / "json").glob("*.json"))
    assert json.loads(json_files[0].read_text(encoding="utf-8")) == {}


def test_prepare_path_sanitizes_label_and_uses_fallback(tmp_path: Path) -> None:
    sanitized = DiagnosticsManager._prepare_path(
        tmp_path,
        "timestamp",
        " route / one ",
        "json",
    )
    fallback = DiagnosticsManager._prepare_path(
        tmp_path,
        "timestamp",
        "***",
        "html",
    )

    assert sanitized.name == "timestamp_route___one.json"
    assert fallback.name == "timestamp_diagnostic.html"
