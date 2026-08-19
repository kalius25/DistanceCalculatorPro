# Sprint 3.7B — VietBanDo Locator + Distance Parser + Engine

Validated rendered DOM contains a stable total-distance element:

```text
#FindPathStatus
```

Examples from the live probe:

```text
Driving: Tổng chiều dài: 128.1 km
Truck:   Tổng chiều dài: 128.441 km
Walking: Tổng chiều dài: 126.774 km
```

The per-step `.distance` elements are intentionally ignored.

## Duration

The current VietBanDo route UI exposes no total route duration. The parser does
not estimate one.

For the normalized `RouteOption`:

```text
duration_text = ""
duration_minutes = 0
raw["duration_available"] = False
```

This is deliberate. Production execution remains disabled until the application
flow explicitly supports a provider whose duration is unavailable.

## Live engine validation

```powershell
python -m scripts.smoke_vietbando_engine
```

Or:

```powershell
python -m scripts.smoke_vietbando_engine --mode driving
python -m scripts.smoke_vietbando_engine --mode truck
python -m scripts.smoke_vietbando_engine --mode walking
```

Expected:

```text
Engine extraction: PASS
Routes parsed: 1
Distance: <value> km
Duration available: False
```

VietBanDo remains:

```text
engine_ready=False
execution_enabled=False
```

until unit quality gate and all three live modes pass.
