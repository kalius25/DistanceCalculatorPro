from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BrowserConfig:
    headless: bool
    timeout: int
    slow_mo: int
    viewport_width: int
    viewport_height: int
    user_agent: str | None