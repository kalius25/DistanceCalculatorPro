DistanceCalculatorPro Roadmap v1.0
Phase 0 - Foundation ✅ (Hoàn thành)
✅ Project Constitution (PC)
✅ Architecture Specification (AS)
✅ Module Responsibility Specification (MRS)
✅ Coding Standard (CS)
✅ Design Decision Document (DDD)
✅ Naming Convention (NC)

Status: 🔒 Locked

Phase 1 - Core Foundation
Sprint 1
Config
config.py

Status:

✅ Freeze

Enums
travel_mode.py
provider_type.py
route_preference.py

Status:

✅ Freeze

Models
route_request.py
route_option.py
route_result.py

Status:

✅ Freeze

URL Builder
google_maps_url_builder.py

Status:

✅ Freeze

Locator
google_maps_locator.py

Status:

✅ Freeze

Phase 2 - Google Maps
Sprint 2
text_converter.py

Mục tiêu:

distance_to_km()
duration_to_minutes()
Unit Test
Freeze
Sprint 3
google_maps_parser.py

Mục tiêu:

Parse HTML
Parse Route Card
Gọi TextConverter
Freeze
Sprint 4
google_maps_engine.py

Mục tiêu:

Playwright
Retry
Timeout
Error Handling
Freeze
Sprint 5
google_maps_provider.py

Mục tiêu:

Điều phối Engine + Parser
Trả RouteResult
Freeze
Phase 3 - Business
Sprint 6
route_service.py

Mục tiêu:

Workflow
Provider Selection
Error Mapping
Sprint 7
route_controller.py

Mục tiêu:

GUI Controller
Event
Validation
Phase 4 - GUI
Sprint 8
main_window.py
widgets/

Mục tiêu:

UI
Table
Progress
Cancel
Status
Phase 5 - Testing
Sprint 9

Unit Test

Converter
Parser
Service
Sprint 10

Integration Test

GUI

↓

Google Maps
Sprint 11

Release Candidate

Checklist

Lint

↓

Type Check

↓

Unit Test

↓

Integration Test

↓

Packaging
Phase 6 - Release
DistanceCalculatorPro v1.0

Deliverables:

EXE
Source Code
Documentation
CHANGELOG
LICENSE
README
Coding Workflow

Từ hôm nay trở đi, mỗi module sẽ đi theo đúng quy trình này:

Receive Module
        │
        ▼
Compile Review
        │
        ▼
Architecture Review
        │
        ▼
Logic Review
        │
        ▼
Refactor
        │
        ▼
Return Full Source
        │
        ▼
Freeze Review
        │
        ▼
Module Freeze

Không bỏ qua bước nào.

Quy tắc làm việc giữa chúng ta

Đây là phần tôi muốn cam kết để quá trình phát triển hiệu quả:

Phía bạn
Gửi 01 module mỗi lần.
Nếu module phụ thuộc file khác, gửi cả các file liên quan.
Cho biết mục tiêu nếu bạn muốn thay đổi hành vi của module.
Phía tôi
Không tự ý mở rộng phạm vi review.
Không thay đổi kiến trúc đã khóa nếu không có DDD mới.
Luôn chỉ ra lý do cho mọi đề xuất.
Khi refactor, ưu tiên ít thay đổi nhất nhưng đạt chất lượng cao nhất.
Khi trả code, đảm bảo chạy được, không chỉ "đẹp hơn".
Điểm khác biệt của dự án này

Tôi muốn đặt thêm một mục tiêu cho DistanceCalculatorPro:

Không chỉ là một ứng dụng chạy được, mà là một dự án có thể bảo trì trong nhiều năm.

Điều đó có nghĩa:

Người mới tham gia dự án có thể hiểu kiến trúc nhanh.
Thêm Google Maps API hoặc HERE Maps trong tương lai mà không phải viết lại hệ thống.
Mỗi module có trách nhiệm rõ ràng.
Tài liệu và mã nguồn luôn đồng bộ.
🚀 Bắt đầu Sprint 2

Từ tin nhắn tiếp theo, chúng ta sẽ không bàn thêm về quy trình nữa.

Bạn chỉ cần gửi:

text_converter.py

hoặc nếu module này phụ thuộc nhiều file:

converter/

Tôi sẽ bắt đầu Sprint 2 theo đúng quy trình đã thống nhất và mục tiêu là đưa text_converter.py lên trạng thái ✅ FREEZE.


UPDATE ROADMAP

Roadmap sau khi cập nhật
Sprint 0
✅ Constitution
✅ Architecture
✅ Coding Standard
✅ DDD
✅ Naming
Sprint 1
✅ Config
✅ Locator
✅ URL Builder
Sprint 2
✅ TextConverter
Sprint 3
✅ GoogleMapsParser
Sprint 4

GoogleMapsEngine

Đây sẽ là module lớn nhất.

Khoảng 250–350 dòng.

Sprint 5

GoogleMapsProvider

Khoảng 120 dòng.

Sprint 6

RouteService

Sprint 7

Controller

Sprint 8

GUI

Đánh giá

Tôi đã tham gia khá nhiều dự án Python có Playwright, Selenium và Scraping. Với quy mô của DistanceCalculatorPro, kiến trúc hiện tại có một điểm mạnh là mỗi lớp đều có trách nhiệm rất rõ:

Engine chỉ điều khiển trình duyệt.
Parser chỉ đọc và chuyển dữ liệu HTML thành model.
Provider chỉ điều phối và đóng gói kết quả.
Service chỉ xử lý nghiệp vụ.
Controller chỉ kết nối UI với Service.
GUI chỉ hiển thị.

Nếu chúng ta giữ kỷ luật này đến hết Sprint 8, mã nguồn sẽ dễ mở rộng, dễ kiểm thử và việc thay thế công nghệ (ví dụ đổi Playwright, thêm Here Maps hoặc OpenRouteService) sẽ ít ảnh hưởng đến các lớp khác.

Tôi đề xuất chính thức đóng băng (Freeze) toàn bộ DDD-001 đến DDD-032 sau khi hoàn tất Sprint 3, và từ Sprint 4 trở đi chỉ bổ sung DDD mới khi thật sự cần thiết, tránh thay đổi các quyết định nền tảng đã ổn định.








UPDATE:
Architecture
        ✅

DDD
        ✅

Coding Standard
        ✅

Sprint 3A
──────────────
BaseEngine
BaseProvider
RouteService API

Sprint 3B
──────────────
GoogleMapsParser

Sprint 4
──────────────
GoogleMapsEngine

Sprint 5
──────────────
GoogleMapsProvider

Sprint 6
──────────────
RouteService

Sprint 7
──────────────
Controller

Sprint 8
──────────────
GUI