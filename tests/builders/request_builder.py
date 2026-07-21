from app.enums.travel_mode import TravelMode
from app.models.route_request import RouteRequest


def make_request(**kwargs):
    data = dict(
        origin="Can Tho",
        destination="Ho Chi Minh",
        timeout=30,
        travel_mode=TravelMode.DRIVING,
    )

    data.update(kwargs)

    return RouteRequest(**data)