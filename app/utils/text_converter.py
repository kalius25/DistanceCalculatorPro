import re


class TextConverter:

    @staticmethod
    def distance_to_km(text: str) -> float:
        """
        61,3 km -> 61.3
        725 m -> 0.725
        """

        text = text.strip().lower()

        if "km" in text:
            value = (
                text.replace("km", "")
                    .replace(",", ".")
                    .strip()
            )
            return float(value)

        if text.endswith("m"):
            value = (
                text.replace("m", "")
                    .replace(",", ".")
                    .strip()
            )
            return float(value) / 1000

        raise ValueError(text)

    @staticmethod
    def duration_to_minutes(text: str) -> int:
        """
        1 giờ 37 p

        45 p

        2 giờ

        """

        text = text.lower()

        hour = 0
        minute = 0

        m = re.search(r"(\d+)\s*giờ", text)
        if m:
            hour = int(m.group(1))

        m = re.search(r"(\d+)\s*p", text)
        if m:
            minute = int(m.group(1))

        return hour * 60 + minute