from app.presentation.widgets.execution_card import ExecutionCard


def test_execution_card_initial_state(qtbot: object) -> None:
    card = ExecutionCard()
    qtbot.addWidget(card)  # type: ignore[attr-defined]

    assert not card.running
    assert not card._action_button.isEnabled()
    assert card._action_button.text() == "Start Calculation"
    assert card._status_label.text() == (
        "Complete workspace configuration first."
    )


def test_execution_card_summary_and_readiness(qtbot: object) -> None:
    card = ExecutionCard()
    qtbot.addWidget(card)  # type: ignore[attr-defined]

    card.set_summary(
        workbook_name="routes.xlsx",
        row_count=300,
        provider="google_maps_web",
        travel_mode="driving",
    )
    card.set_ready(True)

    assert card._workbook_value.text() == "routes.xlsx"
    assert card._rows_value.text() == "300"
    assert card._provider_value.text() == "google_maps_web"
    assert card._travel_mode_value.text() == "Driving"
    assert card._api_calls_value.text() == "300"
    assert card._duration_value.text() == "≈ 1 min"
    assert card._action_button.isEnabled()
    assert card._status_label.text() == "Ready to calculate."


def test_execution_card_start_and_stop_signals(qtbot: object) -> None:
    card = ExecutionCard()
    qtbot.addWidget(card)  # type: ignore[attr-defined]
    card.set_ready(True)

    with qtbot.waitSignal(card.start_requested):  # type: ignore[attr-defined]
        card._action_button.click()

    card.set_running(True)
    assert card.running
    assert card._action_button.text() == "Stop Calculation"
    assert card._status_label.text() == "Calculation is running…"

    with qtbot.waitSignal(card.stop_requested):  # type: ignore[attr-defined]
        card._action_button.click()


def test_execution_card_ignores_readiness_changes_while_running(
    qtbot: object,
) -> None:
    card = ExecutionCard()
    qtbot.addWidget(card)  # type: ignore[attr-defined]
    card.set_running(True)

    card.set_ready(False)

    assert card._action_button.isEnabled()
    assert card._status_label.text() == "Calculation is running…"


def test_execution_duration_handles_empty_and_large_jobs() -> None:
    assert ExecutionCard._estimate_duration(0) == "—"
    assert ExecutionCard._estimate_duration(18_000) == "≈ 60 min"
