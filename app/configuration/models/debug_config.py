from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class DebugConfig:
    save_html: bool
    save_screenshot: bool
    save_json: bool
