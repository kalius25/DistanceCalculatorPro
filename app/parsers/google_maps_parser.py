"""
Google Maps Parser.

Responsibility
--------------
Read route information from a Google Maps result page and convert it into
RouteOption domain models.

The parser must NOT:

- wait for elements
- navigate browser
- retry
- create RouteResult
- know Provider
"""

from __future__ import annotations

import re

from playwright.sync_api import Locator
from playwright.sync_api import Page

from app import config
from app.engines.google_maps_locator import GoogleMapsLocator
from app.models.route_option import RouteOption
from app.utils.text_converter import TextConverter

# =============================================================================
# Internal Regex
# =============================================================================

_DISTANCE_PATTERN = re.compile(
    r"""
    (
        \d+(?:[.,]\d+)?
        \s*
        (?:km|m|mi|ft)
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

_DURATION_PATTERN = re.compile(
    r"""
    (
        (?:\d+\s*(?:giờ|tiếng|h|hr|hrs|hour|hours))
        (?:\s*\d+\s*(?:phút|p|min|mins|minute|minutes))?
        |
        (?:\d+\s*(?:phút|p|min|mins|minute|minutes))
    )
    """,
    re.IGNORECASE | re.VERBOSE,
)

# =============================================================================
# Internal Keywords
# =============================================================================

_TOLL_KEYWORDS = (
    "thu phí",
    "toll",
)

_FERRY_KEYWORDS = (
    "phà",
    "ferry",
)

_HIGHWAY_KEYWORDS = (
    "cao tốc",
    "expressway",
    "highway",
)

_IGNORE_SUMMARY_KEYWORDS = (
    "km",
    "giờ",
    "phút",
    "p",
    "thu phí",
    "chi tiết",
    "xem trước",
    "hr",
    "hour",
    "hours",
    "min",
    "minute",
    "minutes",
    "hrs",
    "mins",
)

# =============================================================================
# Private Helpers
# =============================================================================

def _has_keyword(
    text: str,
    keywords: tuple[str, ...],
) -> bool:
    """Return True if any keyword exists in the given text."""

    lower = text.lower()

    return any(keyword in lower for keyword in keywords)


def _extract_distance(text: str) -> str | None:
    """Extract distance text from a route card."""

    match = _DISTANCE_PATTERN.search(text)

    if not match:
        return None

    return match.group(1)


def _extract_duration(text: str) -> str | None:
    """Extract duration text from a route card."""

    match = _DURATION_PATTERN.search(text)

    if match is None:
        return None
    
    return match.group(1).strip()


def _extract_summary(text: str) -> str:
    """Extract route summary."""

    for line in text.splitlines():

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if any(word in lower for word in _IGNORE_SUMMARY_KEYWORDS):
            continue

        if len(line) < 2:
            continue

        return line

    return ""


def _parse_card(card: Locator) -> RouteOption | None:
    """Convert one Google Maps route card into RouteOption."""

    text = card.inner_text()

    duration_text = _extract_duration(text)
    distance_text = _extract_distance(text)

    if duration_text is None:
        return None

    if distance_text is None:
        return None
    
    summary = _extract_summary(text)

    return RouteOption(
        summary=summary,
        distance_text=distance_text,
        distance_km=TextConverter.distance_to_km(distance_text),
        duration_text=duration_text,
        duration_minutes=TextConverter.duration_to_minutes(duration_text),
        has_toll=_has_keyword(text, _TOLL_KEYWORDS),
        has_ferry=_has_keyword(text, _FERRY_KEYWORDS),
        has_highway=_has_keyword(text, _HIGHWAY_KEYWORDS),
        raw={
            "text": text,
            "summary": summary,
            "distance_text": distance_text,
            "duration_text": duration_text,
        },
    )

# =============================================================================
# Public Parser
# =============================================================================


class GoogleMapsParser:
    """Google Maps route parser."""

    @staticmethod
    def parse(page: Page) -> list[RouteOption]:
        """
        Parse all available routes from the current Google Maps page.

        Parameters
        ----------
        page:
            Playwright page that already contains route results.

        Returns
        -------
        list[RouteOption]
            Parsed routes.
        """

        locator = GoogleMapsLocator.route_cards(page)

        count = min(
            locator.count(),
            config.PARSER_MAX_ROUTES,
        )

        routes: list[RouteOption] = []

        for index in range(count):

            option = _parse_card(locator.nth(index))

            if option is not None:
                routes.append(option)

        return routes


__all__ = [
    "GoogleMapsParser",
]

