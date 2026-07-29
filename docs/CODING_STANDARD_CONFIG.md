
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