Từ bây giờ tôi sẽ áp dụng các quy tắc:

✅ Python 3.11+
✅ PEP8
✅ dataclass(slots=True)
✅ Type Hint đầy đủ
✅ Docstring đầy đủ
✅ Không magic string
✅ Không API cũ
✅ Mỗi file đều có thể thay thế trực tiếp

Mỗi release sẽ đảm bảo
✅ Biên dịch được.
✅ Chạy được.
✅ Test pass.
✅ Không còn API cũ.


Principle 1 — Dependency Direction

Toàn bộ project chỉ được phụ thuộc theo chiều này.

GUI
        │
        ▼
Controller
        │
        ▼
Service
        │
        ▼
Provider
        │
        ▼
Engine
        │
        ▼
Parser
        │
        ▼
Models
        │
        ▼
Enums
        │
        ▼
Constants

Ví dụ

❌ Parser import Service

❌ Engine import Controller

❌ Model import Provider

đều cấm.

Principle 2 — Single Responsibility

Ví dụ

GoogleMapsParser

chỉ có nhiệm vụ

HTML

↓

RouteOption

Không được

ghi log
lưu file
screenshot
sleep
retry

GoogleMapsEngine

chỉ có

Open Browser

↓

Open URL

↓

Wait

↓

Call Parser

CalculationService

chỉ có

Validate

↓

Provider

↓

Best Route

↓

RouteResult
Principle 3 — Zero Magic

Không còn

15000

3000

"Google Maps"

"driving"

"vi"

Mọi thứ đều đi qua

config.py

↓

constants.py

↓

enum.py
Đây là Version 1.0 Architecture Freeze

Từ đây trở đi tôi cam kết:

✅ Không đổi tên class.

✅ Không đổi API.

✅ Không đổi model.

Trừ khi Google Maps thay đổi.











Coding Standard v1.0 (Freeze)
1. Không Hardcode

Ví dụ KHÔNG ĐƯỢC

page.wait_for_timeout(3000)

timeout=15000

"https://www.google.com/maps"

"vi"

"VN"

"driving"

"avoid"

5

2

Thay bằng

PAGE_LOAD_WAIT

PARSER_TIMEOUT

GOOGLE_MAPS_DIRECTIONS_URL

GOOGLE_LANGUAGE

GOOGLE_REGION

TravelMode.DRIVING

RoutePreference.AVOID

PARSER_MAX_ROUTES

MAX_RETRY
2. Có Enum thì không dùng String

Sai

if travel_mode == "driving":

Đúng

if travel_mode is TravelMode.DRIVING:

Sai

if preference == "avoid":

Đúng

if preference is RoutePreference.AVOID:
3. Có Config thì không Hardcode

Ví dụ

Sai

page.goto(url, timeout=30000)

Đúng

page.goto(
    url,
    timeout=BROWSER_TIMEOUT,
)

Sai

page.wait_for_timeout(3000)

Đúng

page.wait_for_timeout(PAGE_LOAD_WAIT)
4. Một nơi duy nhất quản lý Config

Ví dụ

Google Maps URL

chỉ tồn tại trong

config.py

không được xuất hiện nữa trong

Engine

Parser

Provider

Tests
5. Không Duplicate Logic (DRY)

Ví dụ hôm nay

Sai

build()

↓

tự build URL


build_route()

↓

tự build URL

Đúng

build()

↓

build_route()

↓

wrapper

↓

build()
6. Một hàm một nhiệm vụ

Ví dụ

Parser

Không được

Parse

↓

Retry

↓

Save HTML

↓

Screenshot

↓

Logging

Parser chỉ:

HTML

↓

RouteOption
7. Exception không Log

Sai

raise ParserException(...)

logger.error(...)

Đúng

raise ParserException(...)

Engine hoặc Service mới log.

8. Logger duy nhất

Toàn bộ project chỉ dùng

logger = get_logger(__name__)

Không dùng

print()

logging.info()

logging.basicConfig()
9. Mọi Hardcode mới đều phải tự hỏi

Có cần đưa lên

config.py

không?

Ví dụ

Nếu thấy

wait_for_selector(..., timeout=8000)

Tôi sẽ tự hỏi

"Có nên thêm"

SELECTOR_TIMEOUT

vào config không?

Nếu timeout đó chỉ dùng một lần và không cần điều chỉnh, tôi sẽ không đưa lên config.py để tránh phình to.

Nếu timeout được dùng ở nhiều nơi hoặc người dùng có thể muốn thay đổi, tôi sẽ đề xuất đưa vào config.py.

10. Không Over-engineering Config

Đây là điểm rất quan trọng.

Tôi không muốn biến config.py thành một "bãi rác".

Ví dụ

Sai

WINDOW_TITLE

DEFAULT_BUTTON_WIDTH

DEFAULT_MARGIN

DEFAULT_PADDING

DEFAULT_FONT_SIZE

DEFAULT_ICON_SIZE

Nếu chỉ dùng đúng 1 lần, cứ để gần nơi sử dụng.

Chỉ đưa vào config.py khi:

Dùng từ 2 nơi trở lên, hoặc
Có khả năng cần thay đổi theo môi trường (DEV/PROD), hoặc
Là cấu hình nghiệp vụ của ứng dụng.

11. Trong giai đoạn refactor, ưu tiên Backward Compatibility. Chỉ thay đổi public API khi toàn bộ các caller đã được cập nhật.



Cam kết của tôi:
Từ bây giờ, mọi file tôi gửi cho bạn sẽ trải qua quy trình sau trước khi gửi:

✅ Kiểm tra hardcode.
✅ Kiểm tra có thể thay bằng Enum hay không.
✅ Kiểm tra có nên đưa lên config.py hay không.
✅ Kiểm tra logic trùng lặp (DRY).
✅ Kiểm tra đúng SRP (Single Responsibility Principle).
✅ Kiểm tra khả năng tương thích với code hiện tại.
✅ Chỉ khi đạt các tiêu chí trên tôi mới đề xuất thay thế file.

Không hardcode.
Không làm bẩn config.
Không tạo Enum vô ích.
Không được phá vỡ Backward Compatibility nếu chưa refactor xong toàn bộ project.
