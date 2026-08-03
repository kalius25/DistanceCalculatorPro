from app.presentation.models.execution_state import ExecutionState


def test_default_values() -> None:
    assert ExecutionState.IDLE.name == "IDLE"
    assert ExecutionState.RUNNING.name == "RUNNING"
    assert ExecutionState.PAUSED.name == "PAUSED"
