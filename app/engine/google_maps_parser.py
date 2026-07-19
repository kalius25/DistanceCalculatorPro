from __future__ import annotations

import re

from app.models.route_option import RouteOption
from app.models.route_request import RouteRequest
from app.models.route_result import RouteResult
from app.utils.text_converter import TextConverter


class GoogleMapsParser:

    PROVIDER_NAME = "Google Maps Web"

    @classmethod
    def parse(
        cls,
        page,
        request: RouteRequest,
    ) -> RouteResult:

        result = RouteResult(
            success=True,
            request=request,
            provider=cls.PROVIDER_NAME,
        )

        cards = cls.find_route_cards(page)

        for card in cards:

            option = cls.parse_route_card(card)

            if option:
                result.routes.append(option)

        if not result.routes:

            result.success = False
            result.error = "Không tìm thấy tuyến đường."

        return result

    @staticmethod
    def find_route_cards(page):

        page.wait_for_selector(
            "div.XdKEzd",
            timeout=15000,
        )

        locator = page.locator("div.XdKEzd")

        return [
            locator.nth(i)
            for i in range(locator.count())
        ]

    @classmethod
    def parse_route_card(cls, card):

        text = card.inner_text()

        duration = cls.extract_duration(text)

        distance = cls.extract_distance(text)

        if duration is None or distance is None:
            return None

        option = RouteOption()

        option.summary = cls.extract_summary(text)

        option.duration_text = duration
        option.distance_text = distance

        option.duration_minutes = (
            TextConverter.duration_to_minutes(duration)
        )

        option.distance_km = (
            TextConverter.distance_to_km(distance)
        )

        lower = text.lower()

        option.has_toll = (
            "thu phí" in lower
            or "toll" in lower
        )

        option.has_ferry = (
            "phà" in lower
            or "ferry" in lower
        )

        option.has_highway = (
            "cao tốc" in lower
            or "expressway" in lower
            or "highway" in lower
        )

        option.raw = {
            "text": text,
        }

        return option

    @staticmethod
    def extract_duration(text):

        m = re.search(
            r"(\d+\s*giờ(?:\s*\d+\s*p)?|\d+\s*p)",
            text,
            re.IGNORECASE,
        )

        return m.group(1) if m else None

    @staticmethod
    def extract_distance(text):

        m = re.search(
            r"(\d+(?:,\d+)?\s*km|\d+\s*m)",
            text,
            re.IGNORECASE,
        )

        return m.group(1) if m else None

    @staticmethod
    def extract_summary(text):

        lines = [
            line.strip()
            for line in text.splitlines()
            if line.strip()
        ]

        ignore = (
            "km",
            "giờ",
            "phút",
            "p",
            "thu phí",
            "chi tiết",
            "xem trước",
        )

        for line in lines:

            lower = line.lower()

            if any(word in lower for word in ignore):
                continue

            if len(line) < 2:
                continue

            return line

        return ""