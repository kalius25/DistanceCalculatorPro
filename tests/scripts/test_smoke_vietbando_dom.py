from unittest.mock import MagicMock

from app.enums.travel_mode import TravelMode
from scripts import smoke_vietbando_dom as smoke


def test_request_builds_mode_request() -> None:
    request = smoke._request(TravelMode.TRUCK)

    assert request.travel_mode is TravelMode.TRUCK
    assert request.origin == smoke._ORIGIN
    assert request.destination == smoke._DESTINATION


def test_interesting_lines_filters_and_limits() -> None:
    lines = [
        "noise",
        "12 km",
        "35 phút",
        "more noise",
    ]

    assert smoke._interesting_lines("\n".join(lines)) == [
        "12 km",
        "35 phút",
    ]


def test_candidate_results_counts_parseable_text() -> None:
    page = MagicMock()
    locator = MagicMock()
    page.locator.return_value = locator
    locator.count.return_value = 1
    locator.nth.return_value.inner_text.return_value = "Route A\n12 km\n35 phút"

    results = smoke._candidate_results(page)

    assert len(results) == len(smoke._CANDIDATE_SELECTORS)
    assert all(result.count == 1 for result in results)
    assert all(result.parseable == 1 for result in results)


def test_probe_metric_elements_returns_empty_on_error() -> None:
    page = MagicMock()
    page.locator.side_effect = RuntimeError("boom")

    assert smoke._probe_metric_elements(page) == []
