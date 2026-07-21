from app.models.route_models import RouteResult


def test_route_result_defaults():
    result = RouteResult(
        row_number=1,
        origin="A",
        destination="B",
    )

    assert result.row_number == 1
    assert result.origin == "A"
    assert result.destination == "B"
    assert result.distance is None
    assert result.duration is None
    assert result.provider == ""
    assert result.success is True
    assert result.error == ""


def test_route_result_custom_values():
    result = RouteResult(
        row_number=5,
        origin="Can Tho",
        destination="Long Xuyen",
        distance=62.5,
        duration=80,
        provider="Google",
        success=False,
        error="Timeout",
    )

    assert result.distance == 62.5
    assert result.duration == 80
    assert result.provider == "Google"
    assert result.success is False
    assert result.error == "Timeout"