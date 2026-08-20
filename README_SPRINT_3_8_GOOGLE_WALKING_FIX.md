# Sprint 3.8 — Google Maps Walking production fix

The RC2 regression matrix exposed a real production mismatch:

```text
Google Maps Web / walking
Error: Unsupported travel mode: walking
```

`GoogleMapsUrlBuilder` already encodes Walking correctly with:

```text
!3e2
```

and the provider catalog already advertises Walking support. The remaining
block was `GoogleMapsEngine._select_non_default_travel_mode`, which still
rejected every non-Driving mode.

The engine now accepts:

- Driving
- Walking

because both modes are already encoded in the generated URL.

Truck, Bicycling and Transit remain explicitly unsupported.

No regression-matrix expectation was removed.
