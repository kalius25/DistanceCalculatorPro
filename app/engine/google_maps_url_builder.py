from urllib.parse import quote_plus


class GoogleMapsUrlBuilder:
    """Build Google Maps URLs."""

    BASE_URL = "https://www.google.com/maps"

    @classmethod
    def build_search(cls, keyword: str) -> str:
        keyword = quote_plus(keyword)

        return (
            f"{cls.BASE_URL}/search/"
            f"?api=1&query={keyword}"
        )

    @classmethod
    def build_route(
        cls,
        origin: str,
        destination: str,
        travel_mode: str = "driving",
    ) -> str:

        origin = quote_plus(origin)
        destination = quote_plus(destination)

        return (
            f"{cls.BASE_URL}/dir/"
            f"?api=1"
            f"&origin={origin}"
            f"&destination={destination}"
            f"&travelmode={travel_mode}"
        )