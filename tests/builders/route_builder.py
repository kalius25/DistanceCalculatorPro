from app.models.route_option import RouteOption


def make_route(**kwargs):
    data = dict(
        summary="Fastest",
        distance_text="10 km",
        duration_text="15 phút",
        distance_km=10,
        duration_minutes=15,
    )

    data.update(kwargs)

    return RouteOption(**data)