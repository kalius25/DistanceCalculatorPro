"""Browser recovery actions and runtime metrics."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class RecoveryAction(str, Enum):
    """Recovery action selected for a browser failure."""

    NONE = "none"
    REPLACE_PAGE = "replace_page"
    RESTART_BROWSER = "restart_browser"


@dataclass(slots=True)
class BrowserRecoveryMetrics:
    """Mutable counters for one provider/browser lifetime."""

    pages_created: int = 0
    page_failures: int = 0
    navigation_timeouts: int = 0
    browser_restarts: int = 0
    recovery_failures: int = 0


__all__ = ["BrowserRecoveryMetrics", "RecoveryAction"]
