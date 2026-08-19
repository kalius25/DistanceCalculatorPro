# Sprint 3.7A — VietBanDo Provider Foundation

VietBanDo is added as a visible provider foundation.

URL contract implemented exactly as supplied:

```text
https://maps.vietbando.com/maps/?fp=
START_LAT,START_LON|END_LAT,END_LON;MODE;0;0,0
```

Whitespace is removed from latitude/longitude.

Modes:

- Driving = `2`
- Truck = `3`
- Walking = `5`

## UI behavior

VietBanDo exposes:

- Driving
- Truck
- Walking

The other existing providers continue to expose Driving + Walking only.

VietBanDo is intentionally not executable yet:

```text
engine_ready=False
execution_enabled=False
roadmap_sprint="3.7B"
```

Reason: URL generation is known, but production Distance/Duration extraction
must first be validated against the live VietBanDo DOM.

## Next

Sprint 3.7B:

1. live browser navigation validation;
2. DOM/result probe;
3. identify stable Distance/Duration elements;
4. implement locator + parser + engine;
5. live Driving/Truck/Walking smoke;
6. enable production flow only after those gates pass.
