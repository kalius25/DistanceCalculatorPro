from app.enums.provider_type import ProviderType
from app.enums.travel_mode import TravelMode
from app.release.provider_regression_matrix import (
    PROVIDER_REGRESSION_CASES,
    distance_is_success,
    duration_matches_capability,
)


def test_regression_matrix_contains_all_nine_release_cases() -> None:
    assert len(PROVIDER_REGRESSION_CASES) == 9
    assert {
        (case.provider, case.travel_mode) for case in PROVIDER_REGRESSION_CASES
    } == {
        (ProviderType.GOOGLE_MAPS_WEB, TravelMode.DRIVING),
        (ProviderType.GOOGLE_MAPS_WEB, TravelMode.WALKING),
        (ProviderType.BING_MAPS_WEB, TravelMode.DRIVING),
        (ProviderType.BING_MAPS_WEB, TravelMode.WALKING),
        (ProviderType.OPENSTREETMAP_WEB, TravelMode.DRIVING),
        (ProviderType.OPENSTREETMAP_WEB, TravelMode.WALKING),
        (ProviderType.VIETBANDO_WEB, TravelMode.DRIVING),
        (ProviderType.VIETBANDO_WEB, TravelMode.TRUCK),
        (ProviderType.VIETBANDO_WEB, TravelMode.WALKING),
    }


def test_only_vietbando_allows_missing_duration() -> None:
    without_duration = {
        case.provider
        for case in PROVIDER_REGRESSION_CASES
        if not case.duration_required
    }

    assert without_duration == {ProviderType.VIETBANDO_WEB}


def test_distance_success_rejects_error_and_blank_values() -> None:
    assert not distance_is_success(None)
    assert not distance_is_success("")
    assert not distance_is_success(" ERROR: failed")
    assert distance_is_success(128.1)
    assert distance_is_success("128.1")


def test_duration_capability_validation() -> None:
    assert duration_matches_capability(120, required=True)
    assert duration_matches_capability("2:00", required=True)
    assert not duration_matches_capability(None, required=True)
    assert not duration_matches_capability("", required=True)

    assert duration_matches_capability(None, required=False)
    assert duration_matches_capability("", required=False)
    assert not duration_matches_capability(120, required=False)
