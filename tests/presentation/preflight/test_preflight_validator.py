from pathlib import Path
from unittest.mock import patch

import pytest

from app.batch import OutputWriteError
from app.presentation.preflight import BatchPreflightValidator, PreflightPolicy
from app.presentation.preflight.validator import _default_disk_free


def make_policy(**overrides: object) -> PreflightPolicy:
    values: dict[str, object] = {
        "large_batch_job_count": 100,
        "estimated_bytes_per_job": 100,
        "output_size_multiplier": 1.2,
        "minimum_reserved_bytes": 1_000,
    }
    values.update(overrides)
    return PreflightPolicy(**values)  # type: ignore[arg-type]


def test_policy_rejects_invalid_thresholds() -> None:
    with pytest.raises(ValueError):
        PreflightPolicy(large_batch_job_count=0)
    with pytest.raises(ValueError):
        PreflightPolicy(estimated_bytes_per_job=0)
    with pytest.raises(ValueError):
        PreflightPolicy(output_size_multiplier=0.9)
    with pytest.raises(ValueError):
        PreflightPolicy(minimum_reserved_bytes=-1)


def test_preflight_accepts_small_writable_batch(tmp_path: Path) -> None:
    output = tmp_path / "routes.result.xlsx"
    validator = BatchPreflightValidator(
        make_policy(),
        disk_free_resolver=lambda _path: 100_000,
        writable_validator=lambda _path: None,
    )

    result = validator.validate(
        source_path=tmp_path / "routes.xlsx",
        output_path=output,
        estimated_job_count=10,
        source_size_bytes=500,
    )

    assert result.ok
    assert result.issues == ()
    assert result.estimated_output_bytes == 1_000
    assert result.required_free_bytes == 2_200
    assert result.available_bytes == 100_000


def test_preflight_blocks_insufficient_space_and_warns_large_batch(
    tmp_path: Path,
) -> None:
    validator = BatchPreflightValidator(
        make_policy(),
        disk_free_resolver=lambda _path: 2_000,
        writable_validator=lambda _path: None,
    )

    result = validator.validate(
        source_path=tmp_path / "routes.csv",
        output_path=tmp_path / "routes.result.csv",
        estimated_job_count=100,
        source_size_bytes=500,
    )

    assert not result.ok
    assert [issue.code for issue in result.blocking_issues] == [
        "insufficient_disk_space"
    ]
    assert [issue.code for issue in result.warnings] == ["large_batch"]


def test_preflight_reports_unwritable_output_and_unknown_disk_space(
    tmp_path: Path,
) -> None:
    output = tmp_path / "routes.result.xlsx"

    def reject(_path: Path) -> None:
        raise OutputWriteError(output, "write", "access denied")

    def fail_disk(_path: Path) -> int:
        raise OSError("drive unavailable")

    validator = BatchPreflightValidator(
        make_policy(),
        disk_free_resolver=fail_disk,
        writable_validator=reject,
    )
    result = validator.validate(
        source_path=tmp_path / "routes.xlsx",
        output_path=output,
        estimated_job_count=1,
        source_size_bytes=10,
    )

    assert not result.ok
    assert result.available_bytes is None
    assert {issue.code for issue in result.issues} == {
        "output_not_writable",
        "disk_space_unknown",
    }


def test_preflight_uses_default_resolvers_and_source_size(tmp_path: Path) -> None:
    source = tmp_path / "routes.csv"
    source.write_bytes(b"1234")
    output = tmp_path / "nested" / "routes.result.csv"

    result = BatchPreflightValidator(
        PreflightPolicy(
            large_batch_job_count=10,
            estimated_bytes_per_job=1,
            output_size_multiplier=1.0,
            minimum_reserved_bytes=0,
        )
    ).validate(
        source_path=source,
        output_path=output,
        estimated_job_count=1,
    )

    assert result.ok
    assert result.estimated_output_bytes == 4
    assert output.parent.exists()


def test_default_disk_free_walks_to_existing_parent(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing" / "nested" / "result.xlsx"

    with patch(
        "app.presentation.preflight.validator.shutil.disk_usage",
    ) as disk_usage:
        disk_usage.return_value.free = 123_456

        result = _default_disk_free(missing)

    assert result == 123_456
    disk_usage.assert_called_once_with(tmp_path)


@property
def policy(self) -> PreflightPolicy:
    return self._policy


def test_validator_exposes_policy() -> None:
    policy = PreflightPolicy()

    validator = BatchPreflightValidator(
        policy,
        disk_free_resolver=lambda _path: 1_000_000,
        writable_validator=lambda _path: None,
    )

    assert validator.policy is policy
