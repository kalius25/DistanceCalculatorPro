"""
Distance Calculator Pro

Models dùng cho quá trình tính khoảng cách.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

@dataclass(slots=True)
class RouteResult:
    """
    Kết quả sau khi Provider xử lý.
    """

    row_number: int

    origin: str

    destination: str

    distance: Optional[float] = None

    duration: Optional[int] = None

    provider: str = ""

    success: bool = True

    error: str = ""
