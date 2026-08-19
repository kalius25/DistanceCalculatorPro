from unittest.mock import MagicMock

from app.engines.vietbando_locator import VietBanDoLocator


def test_route_distance_uses_stable_total_distance_id() -> None:
    page = MagicMock()

    result = VietBanDoLocator.route_distance(page)

    assert result is page.locator.return_value
    page.locator.assert_called_once_with("#FindPathStatus")
