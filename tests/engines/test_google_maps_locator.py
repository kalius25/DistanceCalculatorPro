from unittest.mock import MagicMock

from app.engines.google_maps_locator import GoogleMapsLocator


def test_search_box():
    page = MagicMock()
    locator = MagicMock()

    page.locator.return_value = locator

    assert GoogleMapsLocator.search_box(page) is locator

    page.locator.assert_called_once_with('input[name="q"]')


def test_search_button():
    page = MagicMock()
    locator = MagicMock()

    page.locator.return_value = locator

    assert GoogleMapsLocator.search_button(page) is locator

    page.locator.assert_called_once_with("#searchbox-searchbutton")


def test_directions_button():
    page = MagicMock()
    locator = MagicMock()

    page.locator.return_value = locator

    assert GoogleMapsLocator.directions_button(page) is locator

    page.locator.assert_called_once_with('button[data-value="Directions"]')


def test_route_input():
    page = MagicMock()
    locator = MagicMock()
    nth_locator = MagicMock()

    page.locator.return_value = locator
    locator.nth.return_value = nth_locator

    assert GoogleMapsLocator.route_input(page, 1) is nth_locator

    page.locator.assert_called_once_with("input[aria-label]")
    locator.nth.assert_called_once_with(1)


def test_transport_driving():
    page = MagicMock()
    locator = MagicMock()

    page.locator.return_value = locator

    assert GoogleMapsLocator.transport_driving(page) is locator

    page.locator.assert_called_once_with('button[data-travel_mode="0"]')


def test_route_panel():
    page = MagicMock()
    locator = MagicMock()

    page.locator.return_value = locator

    assert GoogleMapsLocator.route_panel(page) is locator

    page.locator.assert_called_once_with('div[role="main"]')


def test_route_cards():
    page = MagicMock()
    locator = MagicMock()

    page.locator.return_value = locator

    assert GoogleMapsLocator.route_cards(page) is locator

    page.locator.assert_called_once_with("div.XdKEzd")
