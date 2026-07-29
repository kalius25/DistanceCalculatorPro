from __future__ import annotations

from app.config import AppMode
from app.logging import (
    location_log_policy as policy_module,
)
from app.logging.location_log_policy import (
    LocationLogPolicy,
)


def test_development_logs_sanitized_locations(
    monkeypatch,
):
    monkeypatch.setattr(
        policy_module,
        "APP_MODE",
        AppMode.DEVELOPMENT,
    )

    result = LocationLogPolicy.build(
        origin="0912 345 678",
        destination="user@example.com",
    )

    assert result == {
        "origin": "***5678",
        "destination": "u***@example.com",
    }


def test_production_logs_location_metadata(
    monkeypatch,
):
    monkeypatch.setattr(
        policy_module,
        "APP_MODE",
        AppMode.PRODUCTION,
    )

    result = LocationLogPolicy.build(
        origin="Can Tho",
        destination="Ho Chi Minh City",
    )

    assert result["origin_present"] is True
    assert result["destination_present"] is True
    assert result["origin_length"] == 7
    assert result["destination_length"] == 16
    assert len(result["origin_hash"]) == 16
    assert len(result["destination_hash"]) == 16


def test_production_handles_empty_locations(
    monkeypatch,
):
    monkeypatch.setattr(
        policy_module,
        "APP_MODE",
        AppMode.PRODUCTION,
    )

    result = LocationLogPolicy.build(
        origin=" ",
        destination="",
    )

    assert result["origin_present"] is False
    assert result["destination_present"] is False
    assert result["origin_length"] == 0
    assert result["destination_length"] == 0