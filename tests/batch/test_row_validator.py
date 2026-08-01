import pytest

from app.batch import RouteJobStatus, RowValidator


def test_validator_handles_skipped_same_and_valid_values() -> None:
    validator = RowValidator()

    skipped = validator.validate("", "B")
    assert skipped.status is RouteJobStatus.SKIPPED
    assert skipped.message == "Origin and destination are required."

    same = validator.validate(" A ", " a ")
    assert same.status is RouteJobStatus.DONE
    assert same.distance_km == 0.0

    assert validator.validate("Can Tho", "Ho Chi Minh").status is (
        RouteJobStatus.PENDING
    )
    assert validator.validate("10.5, 106.5", "11, 107").status is (
        RouteJobStatus.PENDING
    )


@pytest.mark.parametrize(
    ("value", "message"),
    [
        ("north,east", "must be numeric"),
        ("91,106", "latitude must be between"),
        ("10,181", "longitude must be between"),
    ],
)
def test_validator_rejects_invalid_coordinate_pairs(
    value: str,
    message: str,
) -> None:
    result = RowValidator().validate(value, "10,106")

    assert result.status is RouteJobStatus.INVALID
    assert result.message is not None
    assert message in result.message
