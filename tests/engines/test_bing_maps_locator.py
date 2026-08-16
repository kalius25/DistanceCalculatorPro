from unittest.mock import MagicMock

from app.engines.bing_maps_locator import BingMapsLocator


def test_route_results_uses_live_route_card_prefix_selector() -> None:
    page = MagicMock()

    result = BingMapsLocator.route_results(page)

    assert result is page.locator.return_value
    page.locator.assert_called_once_with("[class*='routeResultListItemContainer_']")
