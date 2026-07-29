Logging Architecture
LA-001 — Centralized Logging

Toàn bộ project chỉ sử dụng một cấu hình logging duy nhất.

✅ Đúng

from app.logging import logger

hoặc

logger = LoggingManager.get_logger(__name__)

❌ Sai

logging.basicConfig(...)

ở nhiều nơi.

❌ Sai

logging.getLogger(__name__)

tự phát trong từng module.

LA-002 — Layer Responsibility

Mỗi tầng chỉ log đúng trách nhiệm của mình.

Layer	Log gì
Controller	User request
CalculationService	Business flow
Provider	Provider selection
Engine	Browser automation
Parser	Parsing result
Models	Không log

Không log trùng.

LA-003 — Log Exception Once

Một Exception chỉ được ghi log đúng một lần.

Ví dụ

EngineException
        ▲
Provider
        ▲
CalculationService

Chỉ

CalculationService

được

logger.exception(...)

Các tầng dưới chỉ

raise

không log.

LA-004 — Structured Logging

Không log chuỗi tự do.

Ví dụ

❌

Google timeout

Mà log

event=ENGINE_ERROR

provider=GoogleWebProvider

engine=GoogleMapsEngine

origin=...

destination=...

error_code=ENGINE_ERROR

Sau này có thể chuyển sang JSON Logging mà không thay đổi Business Code.

LA-005 — Models Are Pure

Các model

RouteRequest

RouteResult

RouteOption

không được import logging.

Model chỉ chứa dữ liệu.

LA-006 — Logging Configuration Isolation

Toàn bộ cấu hình logging nằm trong package

app/logging/

Business Layer không được biết:

formatter
handler
file path
console
JSON
rotation
LA-007 — Production Ready

Ngay từ đầu chuẩn bị cho:

Rotating File
Daily File
JSON Formatter
ELK
Loki
Cloud Logging

không phải sửa Business Layer.

LA-008 — No Side Effect

Logger không được:

thay đổi RouteResult
swallow exception
retry
raise exception

Logging chỉ ghi nhận thông tin.

Kiến trúc Logging
                     LoggingManager
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
 ConsoleHandler      FileHandler        Future JsonHandler
        │                   │
        └──────────── Formatter ────────────────┘
                            │
                 logger(__name__)
                            │
      ┌─────────────┬──────────────┬──────────────┐
      │             │              │              │
CalculationService Provider Engine Parser