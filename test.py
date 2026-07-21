from app.utils.text_converter import TextConverter

print(TextConverter.distance_to_km("2.5 mi"))
print(TextConverter.distance_to_km("80 mi"))
print(TextConverter.distance_to_km("1 mi"))

from app.parsers.google_maps_parser import _extract_distance

print(_extract_distance("""
Highway 1

1 hr 30 min

80 mi

Toll road
"""))


print("----------------------------------------------------")

from app.parsers.google_maps_parser import (
    _parse_text,
    _extract_distance,
)

from app.utils.text_converter import TextConverter

text = """
Highway 1

1 hr 30 min

80 mi

Toll road
"""

distance = _extract_distance(text)
print(distance)

distance_km = TextConverter.distance_to_km(distance)
print(distance_km)

route = _parse_text(text)
print(route.distance_text)
print(route.distance_km)