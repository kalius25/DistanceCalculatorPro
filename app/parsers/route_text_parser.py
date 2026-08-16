"""Shared text extraction for web-map route summaries."""

from __future__ import annotations

import re
import unicodedata

from app.models.route_option import RouteOption
from app.utils.text_converter import TextConverter

_DISTANCE_PATTERN = re.compile(
    r"(\d+(?:[.,]\d+)?)\s*(km|mi|ft|m)\b",
    re.IGNORECASE,
)
_DURATION_PATTERN = re.compile(
    r"("
    r"(?:\d+\s*(?:hours|hour|hrs|hr|giờ|tiếng|h))"
    r"(?:\s+\d+\s*(?:minutes|minute|mins|min|phút|p))?"
    r"|"
    r"(?:\d+\s*(?:minutes|minute|mins|min|phút|p))"
    r")",
    re.IGNORECASE,
)


def parse_route_text(
    text: str,
    *,
    provider: str,
) -> RouteOption | None:
    """Parse distance and duration from one provider route summary."""
    text = unicodedata.normalize("NFC", text)
    distance_match = _DISTANCE_PATTERN.search(text)
    duration_match = _DURATION_PATTERN.search(text)

    if distance_match is None or duration_match is None:
        return None

    distance_text = distance_match.group(0).strip()
    duration_text = duration_match.group(0).strip()
    distance_km = TextConverter.distance_to_km(distance_text)
    duration_minutes = TextConverter.duration_to_minutes(duration_text)

    if distance_km is None or duration_minutes is None:
        return None

    summary = _summary_line(
        text,
        distance_text=distance_text,
        duration_text=duration_text,
    )
    lower = text.lower()

    return RouteOption(
        summary=summary,
        distance_text=distance_text,
        distance_km=distance_km,
        duration_text=duration_text,
        duration_minutes=duration_minutes,
        has_toll="toll" in lower or "thu phí" in lower,
        has_ferry="ferry" in lower or "phà" in lower,
        has_highway=(
            "highway" in lower
            or "expressway" in lower
            or "cao tốc" in lower
        ),
        raw={
            "provider": provider,
            "text": text,
            "summary": summary,
            "distance_text": distance_text,
            "duration_text": duration_text,
        },
    )


def _summary_line(
    text: str,
    *,
    distance_text: str,
    duration_text: str,
) -> str:
    """Return the first useful non-metric line."""
    ignored = (
        "distance",
        "time",
        "quãng đường",
        "thời gian",
        distance_text.lower(),
        duration_text.lower(),
    )
    for raw_line in text.splitlines():
        line = raw_line.strip()
        lower = line.lower()
        if not line:
            continue
        if any(token in lower for token in ignored):
            continue
        return line
    return ""


__all__ = ["parse_route_text"]
