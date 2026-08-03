from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from playwright.sync_api import Page

from app.models.route_option import RouteOption

from .models import DiagnosticsSettings
from .retention import (
    DiagnosticsRetentionManager,
    DiagnosticsRetentionSnapshot,
)


class DiagnosticsManager:
    """Runtime developer diagnostics with optional browser artifacts."""

    def __init__(self, settings: DiagnosticsSettings | None = None) -> None:
        self._settings = settings or DiagnosticsSettings()
        self._retention = self._make_retention_manager(self._settings)

    @property
    def settings(self) -> DiagnosticsSettings:
        return self._settings

    def update(self, settings: DiagnosticsSettings) -> None:
        self._settings = settings
        self._retention = self._make_retention_manager(settings)

    @property
    def retention_metrics(self) -> DiagnosticsRetentionSnapshot:
        return self._retention.snapshot

    def trace_browser(
        self,
        logger: logging.Logger,
        event: str,
        **details: object,
    ) -> None:
        if not (self._settings.enabled and self._settings.trace_browser):
            return
        logger.debug(event, extra={"event": event, **details})

    def log_routes(
        self,
        logger: logging.Logger,
        routes: list[RouteOption],
    ) -> None:
        if not (self._settings.enabled and self._settings.parser_diagnostics):
            return
        for index, route in enumerate(routes, start=1):
            logger.debug(
                "ROUTE_PARSED",
                extra={
                    "event": "ROUTE_PARSED",
                    "route_index": index,
                    "summary": route.summary,
                    "distance_km": route.distance_km,
                    "duration_minutes": route.duration_minutes,
                    "has_toll": route.has_toll,
                    "has_ferry": route.has_ferry,
                    "has_highway": route.has_highway,
                },
            )

    def capture_page(
        self,
        page: Page,
        *,
        label: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if not self._settings.enabled:
            return
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        base = self._settings.output_directory
        if self._settings.save_html:
            path = self._prepare_path(base / "html", timestamp, label, "html")
            path.write_text(page.content(), encoding="utf-8")
            self._register_artifact(path)
        if self._settings.save_screenshot:
            path = self._prepare_path(base / "screenshots", timestamp, label, "png")
            page.screenshot(path=str(path), full_page=True)
            self._register_artifact(path)
        if self._settings.save_json:
            path = self._prepare_path(base / "json", timestamp, label, "json")
            path.write_text(
                json.dumps(payload or {}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            self._register_artifact(path)

    def _register_artifact(self, path: Path) -> None:
        if path.exists():
            self._retention.register(path)

    @staticmethod
    def _make_retention_manager(
        settings: DiagnosticsSettings,
    ) -> DiagnosticsRetentionManager:
        return DiagnosticsRetentionManager(
            settings.output_directory,
            settings.retention_policy,
        )

    @staticmethod
    def _prepare_path(
        directory: Path,
        timestamp: str,
        label: str,
        suffix: str,
    ) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        safe_label = (
            "".join(
                character if character.isalnum() or character in "-_" else "_"
                for character in label
            ).strip("_")
            or "diagnostic"
        )
        return directory / f"{timestamp}_{safe_label}.{suffix}"
