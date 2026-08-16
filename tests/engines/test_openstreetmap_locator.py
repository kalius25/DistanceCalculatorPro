from unittest.mock import MagicMock

from app.engines.openstreetmap_locator import OpenStreetMapLocator


def test_route_distance_uses_stable_output_id() -> None:
    page = MagicMock()

    result = OpenStreetMapLocator.route_distance(page)

    assert result is page.locator.return_value
    page.locator.assert_called_once_with("#directions_route_distance")


def test_route_duration_uses_stable_output_id() -> None:
    page = MagicMock()

    result = OpenStreetMapLocator.route_duration(page)

    assert result is page.locator.return_value
    page.locator.assert_called_once_with("#directions_route_time")
