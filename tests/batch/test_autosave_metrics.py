from app.batch import AutosaveMetrics


def test_autosave_metrics_record_and_snapshot() -> None:
    metrics = AutosaveMetrics()

    empty = metrics.snapshot
    assert empty.saves_completed == 0
    assert empty.average_save_seconds == 0.0

    metrics.record(4, 2.0)
    metrics.record(-3, -1.0)

    snapshot = metrics.snapshot
    assert snapshot.saves_completed == 2
    assert snapshot.rows_saved == 4
    assert snapshot.last_rows_saved == 0
    assert snapshot.total_save_seconds == 2.0
    assert snapshot.average_save_seconds == 1.0
    assert snapshot.maximum_save_seconds == 2.0
