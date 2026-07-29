EX-007.1 – Configuration Inventory

Trạng thái: 🔄 In Progress

Mục tiêu
Kiểm kê toàn bộ cấu hình trong dự án.
Phân loại cấu hình theo module.
Xác định giá trị nào là configuration, giá trị nào là constant, và giá trị nào là business value.
Chưa refactor bất kỳ dòng code nào.
1. Quy tắc phân loại
1. Configuration (đưa vào Config)

Là các giá trị có thể thay đổi theo:

môi trường
người dùng
máy tính
phiên bản
nhu cầu sử dụng

Ví dụ:

HEADLESS = True
DEFAULT_TIMEOUT = 30
LOG_LEVEL = "INFO"
EXPORT_FOLDER = "./output"

=> Đưa vào Config.

2. Constant (không đưa vào Config)

Là các giá trị mang tính chuẩn của chương trình.

Ví dụ

GOOGLE_MAPS_BASE_URL

LOG_EVENT_NAME

DEFAULT_SHEET_NAME

SUPPORTED_PROVIDER

Đây là hằng số.

Không nên cho người dùng chỉnh.

3. Business Value

Ví dụ

RouteOption.rank

TravelMode.DRIVING

ProviderType.GOOGLE_WEB

Đây là Domain Model.

Không phải Config.

2. Inventory hiện tại

Dựa trên kiến trúc hiện nay, tôi đề xuất phân loại như sau.

Application
Cấu hình	Đưa vào Config	Ghi chú
Debug Mode	✅	Có
App Version	❌	Constant
Temp Folder	✅	Có
Output Folder	✅	Có
Browser
Cấu hình	Đưa vào Config
Headless	✅
Browser Timeout	✅
Slow Motion	✅
Viewport Width	✅
Viewport Height	✅
User Agent	✅
Google Maps
Cấu hình	Đưa vào Config
Navigation Timeout	✅
Wait Selector Timeout	✅
Retry Count	✅

Không đưa

https://www.google.com/maps

vì đây là constant của Provider.

Logging

Đã hoàn thành ở EX-006

Có thể quản lý

Cấu hình	Đưa vào Config
Log Level	✅
Log Folder	✅
Log File Name	✅
Excel
Cấu hình	Đưa vào Config
Default Sheet Name	❌
Export Folder	✅
Auto Width	✅
Debug
Cấu hình	Đưa vào Config
Save HTML	✅
Save Screenshot	✅
Save Debug JSON	✅
Calculation
Cấu hình	Đưa vào Config
Max Route Count	❌
Ranking Rule	❌

Đây là Business Rule.

Không nên Config.

Provider
Cấu hình	Đưa vào Config
Retry Count	✅
Retry Delay	✅
Default Provider	✅
3. Không nên đưa vào Config

Những thứ sau nên giữ nguyên:

Enums

Error Codes

Log Event Name

Exception Name

Model

RouteResult

TravelMode

ProviderType

Đây là Domain.

4. Cấu trúc Config mục tiêu

Sau EX-007 sẽ hướng tới:

AppConfig
│
├── ApplicationConfig
│
├── BrowserConfig
│
├── ProviderConfig
│
├── LoggingConfig
│
├── ExcelConfig
│
└── DebugConfig

Không tạo:

RouteConfig

vì Route là Business.

5. Danh sách dự kiến cần refactor

Đây là checklist cho EX-007.6:

🔲 headless=True
🔲 timeout=...
🔲 retry_count=...
🔲 slow_mo=...
🔲 viewport=(...)
🔲 log_level=...
🔲 log_directory=...
🔲 output_folder=...
🔲 save_html=...
🔲 save_screenshot=...
6. Tiêu chí hoàn thành EX-007.1
✅ Hoàn thành kiểm kê toàn bộ cấu hình.
✅ Phân biệt rõ Configuration, Constant và Business Value.
✅ Xác định cấu trúc AppConfig sẽ sử dụng ở các bước sau.
✅ Chưa thay đổi bất kỳ hành vi hay mã nguồn nào.

Kết quả: EX-007.1 hoàn thành khi tài liệu inventory này được chốt. Sau đó chúng ta sẽ chuyển sang EX-007.2 – Configuration Models, nơi bắt đầu xây dựng các @dataclass cấu hình nhưng vẫn chưa tác động đến Business Layer.