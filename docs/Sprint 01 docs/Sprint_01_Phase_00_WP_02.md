Sprint 1 – Phase 0
WP-0.2 Architecture Inventory

Status

COMPLETED (Draft v1)
1. Kiến trúc tổng thể

Kiến trúc hiện tại của DistanceCalculatorPro có dạng nhiều lớp (layered architecture) và khá rõ ràng.

Luồng nghiệp vụ hiện tại có thể mô tả như sau:

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
Playwright / Google Maps
    │
    ▼
Parser
    │
    ▼
Model

Song song với luồng trên là các thành phần hỗ trợ:

Enums
Exceptions
Utils
Config

Đây là kiến trúc phù hợp để mở rộng nhiều Provider trong tương lai.

2. Vai trò của từng Package
app/controllers

Đã phát hiện:

calculation_controller.py
Responsibility

Điều phối yêu cầu từ GUI.

Không nên chứa business logic.

Đánh giá

🟢 Đúng vai trò.

app/services

Các module chính:

batch_calculation_service.py
calculation_service.py
excel_service.py
route_service.py
Responsibility

Business Logic.

Service là nơi orchestration.

Đánh giá

🟢 Đây sẽ là Layer trung tâm của hệ thống.

app/providers

Hiện có

base_provider.py
google_web_provider.py
Responsibility

Provider chỉ giao tiếp với nguồn dữ liệu.

Không nên biết Excel.

Không nên biết GUI.

Đánh giá

🟢 Đúng hướng.

Đây sẽ là nơi chuẩn hóa bằng Module Contract.

app/engines

Các thành phần:

browser_manager.py
google_maps_engine.py
google_maps_locator.py
google_maps_url_builder.py
base_engine.py
Responsibility

Làm việc trực tiếp với Playwright.

Browser automation.

DOM interaction.

Đánh giá

🟢 Đây là lớp hạ tầng (Infrastructure Layer).

app/parsers

Hiện có:

google_maps_parser.py
Responsibility

Tách HTML thành dữ liệu.

Đây là quyết định kiến trúc rất tốt vì:

Engine không cần hiểu DOM.

app/models

Đã phát hiện:

route_request.py
route_result.py
route_models.py
route_option.py
excel_table_model.py
debug_report.py
Responsibility

DTO / Data Models.

Đánh giá

🟢 Rất tốt.

app/enums

Các enum:

provider_type
travel_mode
route_preference
Responsibility

Chuẩn hóa giá trị hệ thống.

app/exceptions

Có:

base_exception
engine_exception
parser_exception
provider_exception
Responsibility

Exception phân tầng.

Đây là điểm cộng.

app/utils

Có:

logger.py
text_converter.py
Responsibility

Utility thuần.

Không chứa business logic.

3. Dependency Inventory

Qua phân tích import ban đầu, dependency mong muốn là:

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

Model được dùng xuyên suốt nhưng không điều khiển luồng.

4. Module Ownership
Package	Owner
controllers	Workflow
services	Business Logic
providers	External Provider
engines	Browser Automation
parsers	HTML Parsing
models	Data
enums	Constants
exceptions	Error Handling
utils	Utilities

Tôi đề xuất đây sẽ là bảng Owner chính thức trong tài liệu dự án.

5. Boundary Rules (Đề xuất)

Đây là phần tôi muốn đưa vào Module Contract.

GUI

Được phép

gọi Controller

Không được

gọi Provider
gọi Browser
Controller

Được phép

gọi Service

Không được

parse HTML
Service

Được phép

gọi Provider
gọi Excel

Không được

thao tác Playwright trực tiếp
Provider

Được phép

gọi Engine

Không được

ghi Excel
cập nhật GUI
Engine

Được phép

Browser
DOM

Không được

xử lý nghiệp vụ
Parser

Được phép

HTML → Model

Không được

mở Browser
6. Architecture Strengths

Điểm mạnh hiện tại:

Phân tầng rõ.
Có Base Engine.
Có Base Provider.
Có Exception riêng.
Có Enum riêng.
Có Model riêng.
Có Parser riêng.

Đây là nền tảng rất tốt để tiếp tục.

7. Architecture Risks

Hiện tôi đánh giá các mức rủi ro như sau:

Module	Risk	Nhận xét
Models	🟢 Thấp	Chủ yếu là DTO, ít phụ thuộc.
Enums	🟢 Thấp	Ổn định.
Exceptions	🟢 Thấp	Thiết kế rõ ràng.
Utils	🟢 Thấp	Phạm vi nhỏ.
Parsers	🟡 Trung bình	Phụ thuộc cấu trúc Google Maps, dễ bị ảnh hưởng khi giao diện thay đổi.
Engines	🟡 Trung bình	Gắn với Playwright và DOM automation.
Providers	🟡 Trung bình	Cần chuẩn hóa interface và DistanceResult.
Services	🟡 Trung bình	Là lớp điều phối trung tâm, mọi thay đổi cần kiểm soát kỹ.
Controllers	🟢 Thấp	Hiện khá mỏng, đúng vai trò.
8. Kết luận

Sau WP-0.2, tôi có thể khẳng định:

Kiến trúc hiện tại đủ tốt để tiếp tục phát triển, không cần viết lại từ đầu.
Hướng đi đúng của Sprint 1 là chuẩn hóa (standardize) chứ không tái cấu trúc (rewrite).
Các thay đổi sẽ tập trung vào việc thống nhất model, interface, logging, settings và tài liệu kiến trúc, đồng thời giữ nguyên các ranh giới giữa các layer.
Bước tiếp theo

Tôi đề xuất tiếp tục với WP-0.3 – Quality & Dependency Analysis, trong đó sẽ phân tích chi tiết:

Circular imports.
Dependency Matrix giữa các module.
Dead code và module không còn sử dụng.
Duplicate models/exceptions.
Layer violations (nếu có).
Technical Debt và danh sách ưu tiên xử lý trong Sprint 1.

Đây sẽ là báo cáo cuối cùng của Phase 0 trước khi chúng ta chuyển sang Phase 1 – Implementation.