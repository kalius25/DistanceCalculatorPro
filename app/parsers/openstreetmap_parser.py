"""OpenStreetMap route-result parser."""

from __future__ import annotations

import re

from playwright.sync_api import Page

from app.diagnostics import DiagnosticsManager
from app.engines.openstreetmap_locator import OpenStreetMapLocator
from app.logging import LoggingManager
from app.models.route_option import RouteOption
from app.utils.text_converter import TextConverter

logger = LoggingManager.get_logger(__name__)

_CLOCK_DURATION = re.compile(r"^(\d+):(\d{1,2})$")


def _duration_to_minutes(text: str) -> int | None:
    """Convert OSM ``hours:minutes`` or textual duration to minutes."""
    value = text.strip()
    match = _CLOCK_DURATION.fullmatch(value)
    if match is not None:
        hours = int(match.group(1))
        minutes = int(match.group(2))
        if minutes >= 60:
            return None
        return hours * 60 + minutes

    return TextConverter.duration_to_minutes(value)


class OpenStreetMapParser:
    """Extract the normalized total route from OpenStreetMap."""

    @staticmethod
    def parse(
        page: Page,
        diagnostics: DiagnosticsManager | None = None,
    ) -> list[RouteOption]:
        """Parse the live OSM total Distance and Time outputs."""
        distance_text = OpenStreetMapLocator.route_distance(page).inner_text().strip()
        duration_text = OpenStreetMapLocator.route_duration(page).inner_text().strip()

        distance_km = TextConverter.distance_to_km(distance_text)
        duration_minutes = _duration_to_minutes(duration_text)

        routes: list[RouteOption] = []
        if distance_km is not None and duration_minutes is not None:
            routes.append(
                RouteOption(
                    distance_text=distance_text,
                    distance_km=distance_km,
                    duration_text=duration_text,
                    duration_minutes=duration_minutes,
                    raw={
                        "provider": "openstreetmap_web",
                        "distance_text": distance_text,
                        "duration_text": duration_text,
                    },
                )
            )

        if diagnostics is not None:
            diagnostics.log_routes(logger, routes)
        return routes


__all__ = ["OpenStreetMapParser"]
