from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class LoggingConfig:
    level: str
    directory: str
    filename: str
