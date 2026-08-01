from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppMetadata:
    """Immutable application identity shown by the presentation layer."""

    name: str = "DistanceCalculatorPro"
    version: str = "1.2.0-alpha19"
    organization: str = "DistanceCalculatorPro"
    domain: str = "distancecalculatorpro.local"
