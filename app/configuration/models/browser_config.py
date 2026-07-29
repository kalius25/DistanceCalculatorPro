from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class BrowserConfig:
    """
    Immutable browser runtime configuration.

    Attributes
    ----------
    headless:
        Run the browser without a visible user interface.
    timeout:
        Default Playwright timeout in milliseconds.
    slow_mo:
        Delay in milliseconds between Playwright operations.
    viewport_width:
        Browser viewport width in pixels.
    viewport_height:
        Browser viewport height in pixels.
    user_agent:
        Optional custom browser user-agent.
    locale:
        Browser context locale, such as ``vi-VN``.
    """

    headless: bool
    timeout: int
    slow_mo: int
    viewport_width: int
    viewport_height: int
    user_agent: str | None
    locale: str