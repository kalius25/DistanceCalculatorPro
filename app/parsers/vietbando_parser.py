"""VietBanDo route-result parser."""

from __future__ import annotations

import re

from playwright.sync_api import Page

from app.diagnostics import DiagnosticsManager
from app.engines.vietbando_locator import VietBanDoLocator
from app.logging import LoggingManager
from app.models.route_option import RouteOption
from app.utils.text_converter import TextConverter

logger = LoggingManager.get_logger(__name__)

_TOTAL_DISTANCE_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(km|m)\b",
    re.IGNORECASE,
)


def _extract_distance_text(text: str) -> str | None:
    """Extract the total route metric from VietBanDo summary text."""
    match = _TOTAL_DISTANCE_PATTERN.search(text)
    if match is None:
        return None
    return f"{match.group(1)} {match.group(2)}"


class VietBanDoParser:
    """Extract the normalized total route distance from VietBanDo."""

    @staticmethod
    def parse(
        page: Page,
        diagnostics: DiagnosticsManager | None = None,
    ) -> list[RouteOption]:
        """Parse VietBanDo total distance.

        VietBanDo's current web result does not expose a route duration.
        Duration therefore remains empty/zero rather than being estimated.
        """
        summary_text = VietBanDoLocator.route_distance(page).inner_text().strip()
        distance_text = _extract_distance_text(summary_text)
        routes: list[RouteOption] = []

        if distance_text is not None:
            distance_km = TextConverter.distance_to_km(distance_text)
            if distance_km is not None:
                routes.append(
                    RouteOption(
                        summary=summary_text,
                        distance_text=distance_text,
                        distance_km=distance_km,
                        duration_text="",
                        duration_minutes=0,
                        raw={
                            "provider": "vietbando_web",
                            "summary_text": summary_text,
                            "distance_text": distance_text,
                            "duration_available": False,
                        },
                    )
                )

        if diagnostics is not None:
            diagnostics.log_routes(logger, routes)
        return routes


__all__ = ["VietBanDoParser"]
