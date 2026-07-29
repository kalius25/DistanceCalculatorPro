
Coding Standard mới

Đến thời điểm này, chúng ta đã chính thức bổ sung các quy tắc:

CFG-001

Chỉ ConfigurationLoader được tạo AppConfig.

CFG-002

Chỉ Composition Root được phép gọi ConfigurationLoader.load().

CFG-003

Không sử dụng Global Config.

CFG-004

Ưu tiên truyền đúng Configuration Section thay vì toàn bộ AppConfig.

CFG-005

Configuration phải immutable.

@dataclass(frozen=True)
CFG-006

Loader không chứa:

validation
logging
business logic
environment
file parsing
CFG-007

Không đọc JSON/YAML/ENV ngoài Loader.

CFG-008 ✅

Tất cả Configuration Models đều dùng

@dataclass(frozen=True, slots=True)


CFG-009 – Configure infrastructure at Composition Root

Infrastructure component phải được cấu hình tại composition root bằng đúng configuration section mà nó cần.

Ví dụ đúng:

LoggingManager.configure(
    app_config.logging,
)

Không đúng:

LoggingManager.configure(
    ConfigurationLoader.load().logging,
)

Không đúng:

LoggingManager.configure(
    app_config,
)
CFG-010 – No configuration loading inside infrastructure

Infrastructure không được tự gọi:

ConfigurationLoader.load()

Configuration phải được truyền từ bên ngoài.

CFG-011 – Configuration units must be explicit

Giá trị cấu hình có đơn vị phải được mô tả rõ trong model hoặc tên field.

Ví dụ:

timeout: int  # milliseconds
slow_mo: int  # milliseconds
viewport_width: int  # pixels

Trong phiên bản sau có thể đổi tên rõ hơn:

timeout_ms
slow_mo_ms

Nhưng để giảm phạm vi refactor hiện tại, vẫn giữ tên field cũ và ghi rõ đơn vị trong docstring.

CFG-012 – Transitional fallback must be removable

Compatibility fallback trong quá trình Dependency Tree phải:

nằm trong một method riêng;
có docstring ghi rõ là tạm thời;
có test riêng;
không được lan sang Business Layer;
phải bị xóa khi dependency phía trên đã được inject.

Áp dụng:

BrowserManager._create_legacy_config()

Sẽ bị xóa tại bước refactor GoogleWebProvider hoặc composition root.

CFG-013 – Transitional compatibility lasts exactly one dependency level

Compatibility fallback chỉ được phép tồn tại để bảo vệ nút kế tiếp trong Dependency Tree.

Ví dụ:

BrowserManager

↓

GoogleWebProvider

Sau khi GoogleWebProvider refactor xong thì:

_create_legacy_config()

phải bị xóa ngay.

Không được để:

BrowserManager

↓

GoogleWebProvider

↓

CalculationService

↓

Controller

↓

UI

mà fallback vẫn còn.

Nói cách khác:

Không có compatibility code nào được phép sống quá một bước refactor.

Đây là nguyên tắc rất quan trọng giúp dự án không tích tụ "nợ kỹ thuật tạm thời".




DI-001 – Required dependencies are constructor parameters

Dependency bắt buộc phải là tham số bắt buộc trong constructor.

Đúng:

def __init__(
    self,
    browser: BrowserManager,
    engine: GoogleMapsEngine,
) -> None:

Không đúng:

def __init__(
    self,
    browser: BrowserManager | None = None,
    engine: GoogleMapsEngine | None = None,
) -> None:
DI-002 – Injected dependencies are not recreated

Một class không được thay thế dependency đã inject bằng instance do nó tự tạo.

Không đúng:

self._engine = engine or GoogleMapsEngine()

Đúng:

self._engine = engine
DI-003 – Dependency assembly belongs outside business components

Các component như Provider, Service, Controller không được tự lắp ráp dependency graph.

Assembly cuối cùng thuộc Composition Root.