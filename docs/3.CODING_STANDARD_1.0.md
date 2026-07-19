DistanceCalculatorPro Coding Standard v1.0
A. Architecture Rules (AR)
AR-01. Layer Dependency

Chỉ được phụ thuộc theo một chiều:

GUI
↓
Controller
↓
Service
↓
Provider
↓
Engine
↓
Parser
↓
Converter
↓
Models
↓
Enums
↓
Constants

Không được phụ thuộc ngược.

AR-02. Single Responsibility

Mỗi module chỉ có một nhiệm vụ.

Ví dụ:

Parser → Parse HTML
Converter → Convert dữ liệu
Engine → Điều khiển Browser
Provider → Cung cấp dữ liệu
Service → Business Logic
AR-03. Backward Compatibility

Trong quá trình refactor:

Không phá API cũ.
Chỉ xóa API khi toàn bộ caller đã chuyển sang API mới.

Ví dụ:

build_route(...)

được giữ làm wrapper.

B. Configuration Rules (CR)
CR-01. Không Hardcode

Không hardcode:

URL
Timeout
Retry
Language
Region

Đưa vào config.py.

CR-02. Một nơi quản lý Config

Toàn bộ cấu hình chỉ tồn tại trong:

config.py
CR-03. Không biến config thành "bãi rác"

Không đưa vào config:

CSS selector
Regex
Keyword
UI margin
Padding

Chỉ đưa vào khi:

dùng nhiều nơi
cần thay đổi theo môi trường
là cấu hình nghiệp vụ
C. Locator Rules (LR)
LR-01. Selector tập trung

Mọi CSS/XPath chỉ tồn tại trong:

google_maps_locator.py
LR-02. Parser không được chứa selector

Sai:

page.locator(...)

Đúng:

GoogleMapsLocator.route_cards(page)
LR-03. Dùng Locator.wait_for()

Không:

page.wait_for_selector(...)

Nếu đã có Locator.

D. Parser Rules (PR)
PR-01. Parser chỉ Parse

Parser chỉ lấy:

HTML

↓

Raw Text

Không convert.

PR-02. Parser không Retry

Retry thuộc:

Engine

Provider

PR-03. Parser không Log

Không:

logger.error(...)
PR-04. Parser không Convert

Không:

350 m

↓

0.35

Parser chỉ lấy

350 m
PR-05. Parser không chứa Business Logic

Ví dụ:

Không:

if distance > ...
E. Converter Rules (CV)
CV-01. Converter chỉ Convert

Ví dụ

350 m

↓

0.35 km
CV-02. Converter là Pure Function

Không:

sleep
logger
print
network
CV-03. Converter không Raise

Sai:

raise ValueError

Đúng:

None
CV-04. Converter hỗ trợ mọi format Google

Ví dụ:

350 m
1 km
1.2 km
1,2 km
15 mi
500 ft
F. Data Rules (DR)
DR-01. Canonical Storage Unit

Toàn bộ hệ thống lưu:

Distance

↓

Kilometer
DR-02. Display Unit tách biệt

GUI có thể hiển thị:

m

km

mi

ft

Nhưng storage luôn là km.

DR-03. Raw Text phải giữ nguyên

Ví dụ

distance_text

luôn giữ đúng Google.

G. Enum Rules (ER)
ER-01. Có Enum thì không dùng String

Sai

"driving"

Đúng

TravelMode.DRIVING
ER-02. Không tạo Enum vô ích

Ví dụ

Không tạo

AvoidKeyword
H. Constant Rules (KR)
KR-01. Internal Constant

Regex

Keyword

Selector

để ngay đầu file.

Không đưa Config.

KR-02. Regex là Internal Constant

Ví dụ

_DISTANCE_PATTERN
_DURATION_PATTERN
KR-03. Keyword là Internal Constant

Ví dụ

_TOLL_KEYWORDS

_FERRY_KEYWORDS
I. Code Rules (CD)
CD-01. DRY

Không duplicate logic.

Ví dụ

build()

↓

build_route()

↓

wrapper

↓

build()
CD-02. Readability > Clever Code

Ưu tiên

if:
    append()

thay vì list comprehension phức tạp nếu không mang lại lợi ích rõ ràng.

CD-03. Type Hint đầy đủ

Public function luôn có type hint.

CD-04. Public Method có Docstring

Private method không bắt buộc.

J. Logging & Exception Rules (LE)
LE-01. Exception không Log

Raise thôi.

Caller log.

LE-02. Logger duy nhất

Toàn project

logger = get_logger(__name__)
LE-03. Không print()

Không dùng

print()
K. Future Extension Rules (FR)
FR-01. Formatter chỉ hiển thị

Ví dụ

20.1168 km

↓

12.5 mi
FR-02. UI không tính toán

UI chỉ hiển thị.

Không convert.

Tổng kết
Nhóm	Nội dung
AR	Architecture
CR	Configuration
LR	Locator
PR	Parser
CV	Converter
DR	Data Model & Storage
ER	Enum
KR	Internal Constant
CD	Code Quality
LE	Logging & Exception
FR	Future Extension