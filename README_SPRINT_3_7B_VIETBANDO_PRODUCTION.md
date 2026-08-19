# Sprint 3.7B — VietBanDo Production Integration

VietBanDo is now registered in the production provider router for:

- Driving
- Truck
- Walking

The provider is marked:

```text
engine_ready=True
execution_enabled=True
```

## Missing duration contract

VietBanDo exposes route distance but not route duration. The application does
not estimate duration.

When the parsed route has:

```text
raw["duration_available"] = False
```

the batch service records:

```text
result_distance_km = <distance>
result_duration_minutes = None
result_duration_text = None
```

Therefore `Result distance` is written normally and `Result duration` remains
blank.

## Production smoke

```powershell
python -m scripts.smoke_vietbando_production_flow --mode driving
python -m scripts.smoke_vietbando_production_flow --mode truck
python -m scripts.smoke_vietbando_production_flow --mode walking
```

## GUI acceptance

```powershell
python -m scripts.smoke_vietbando_gui_acceptance --mode driving
python -m scripts.smoke_vietbando_gui_acceptance --mode truck
python -m scripts.smoke_vietbando_gui_acceptance --mode walking
```

Expected GUI output:

```text
GUI acceptance: PASS
Result distance: <number>
Result duration: None
```
