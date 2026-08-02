from __future__ import annotations

import pytest

from app.batch.autosave_policy import AutoSavePolicy


def test_autosave_policy_uses_row_and_time_thresholds() -> None:
    now = [10.0]
    policy = AutoSavePolicy(2, 30.0, clock=lambda: now[0])

    assert not policy.should_save()
    policy.record_write()
    assert policy.dirty_rows == 1
    assert not policy.should_save()

    now[0] = 41.0
    assert policy.should_save()
    policy.mark_saved()
    assert policy.dirty_rows == 0
    assert not policy.should_save()

    policy.record_write()
    policy.record_write()
    assert policy.should_save()


def test_autosave_policy_rejects_invalid_intervals() -> None:
    with pytest.raises(ValueError, match="row_interval"):
        AutoSavePolicy(0, 1.0)
    with pytest.raises(ValueError, match="seconds_interval"):
        AutoSavePolicy(1, 0.0)
