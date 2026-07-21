SOFTWARE SPECIFICATION
Software Specification v1.0.3 (Frozen)

Version: 1.0 Draft
Platform: Windows Desktop
GUI Framework: PySide6 (Qt)
Ngôn ngữ: Python 3.x

1. Mục tiêu

DistanceCalculatorPro là phần mềm Desktop dùng để tính khoảng cách giữa hai tọa độ địa lý từ dữ liệu Excel thông qua nhiều Provider định tuyến (Google Web, Google Routes API, HERE, OSRM, Mapbox...).

Mục tiêu của phần mềm:

Tốc độ xử lý cao.
Hỗ trợ xử lý hàng chục nghìn dòng dữ liệu.
Resume sau khi dừng.
Không làm thay đổi dữ liệu gốc của Excel.
Dễ mở rộng Provider.
Dễ bảo trì và phát triển lâu dài.
2. Kiến trúc tổng thể
GUI
    │
    ▼
Controller
    │
    ▼
Worker Thread
    │
    ▼
BatchCalculationService
    │
    ▼
ProviderFactory
    │
    ├── GoogleWebProvider
    ├── GoogleRoutesProvider
    ├── HEREProvider
    ├── OSRMProvider
    └── ...
    │
    ▼
DistanceResult

Nguyên tắc:

GUI không gọi Provider trực tiếp.
GUI chỉ giao tiếp với Controller.
Controller chỉ gọi Service.
Service chỉ làm việc với Interface của Provider.
3. Công nghệ sử dụng
Thành phần	Công nghệ
GUI	PySide6
Excel	openpyxl
Browser Automation	Playwright
Logging	logging
Build	PyInstaller
Settings	JSON
4. Thiết kế giao diện
4.1 Input
Browse Excel
Workbook
Sheet Dropdown
Preview 20 dòng đầu

Hiển thị:

Tổng số dòng
Tổng số cột
Số dòng đã xử lý
Số dòng cần xử lý
4.2 Configuration

Cho phép cấu hình:

Provider
Travel Mode
Route Preference
Ferry
Retry
Delay
Resume
4.3 Execution

Bao gồm:

Progress Bar
ETA
Log
Start
Stop
Open Excel
5. Quy chuẩn Excel
5.1 Input

Bắt buộc có đúng 4 cột:

OriginLat
OriginLng
DestinationLat
DestinationLng

Không hỗ trợ Mapping.

5.2 Output

Phần mềm sẽ ghi các cột sau:

Distance
Duration
Traffic
Toll
Ferry
Status
Provider
RouteURL
Timestamp

Ý nghĩa:

Cột	Ý nghĩa
Distance	Khoảng cách
Duration	Thời gian (phút)
Traffic	Mức độ giao thông (nếu Provider hỗ trợ)
Toll	Có đi qua đường thu phí
Ferry	Có đi qua phà
Status	Trạng thái xử lý
Provider	Provider sử dụng
RouteURL	Link mở Google Maps
Timestamp	Thời điểm xử lý
5.3 Duration

Đơn vị lưu:

Minute

Ví dụ

125

Không lưu

2 giờ 05 phút
5.4 Skip Rule

Nếu cột

Distance

đã có dữ liệu

↓

Không tính lại.

Status ghi

SKIPPED
5.5 Không được thay đổi

Phần mềm tuyệt đối không được thay đổi:

Font
Cell Color
Width
Height
Formula
Filter
Freeze Pane
Sheet khác

Ngoài các cột Output.

6. Preview

Sau khi mở Workbook:

↓

Đọc danh sách Sheet

↓

Người dùng chọn Sheet

↓

Preview 20 dòng đầu.

Hiển thị:

Rows
Columns
Need Processing
Already Processed
7. Chuẩn Provider

Mọi Provider đều phải trả về chung một đối tượng:

DistanceResult

Ví dụ:

DistanceResult(
    distance,
    duration,
    traffic,
    toll,
    ferry,
    status,
    provider,
    route_url,
    timestamp
)

GUI hoàn toàn không biết Provider cụ thể.

8. Google Web Provider

Google Web phải lấy được:

Distance
Duration
Traffic
Toll
Ferry
RouteURL

Trong đó:

Duration

↓

Luôn chuyển sang phút.

9. Resume

Mặc định:

Distance != Empty

↓

Skip

Không tính lại.

10. Retry

Retry theo Settings.

Nếu Retry vượt giới hạn

↓

Status

TIMEOUT

Sau đó tiếp tục dòng kế tiếp.

11. Error Code

Toàn bộ phần mềm chỉ sử dụng bộ mã trạng thái sau:

OK
SKIPPED
INVALID_COORDINATE
TIMEOUT
NO_ROUTE
UNKNOWN

Không sử dụng tiếng Việt trong Status.

Các mã này được dùng thống nhất tại:

Excel
Log
Popup Summary
Debug Log
Provider
12. Logging

Thông thường chỉ hiển thị ngắn gọn:

Row 100 OK

Nếu lỗi

↓

Log phải ghi đầy đủ:

Row Number

OriginLat

OriginLng

DestinationLat

DestinationLng

Provider

Retry Count

Error Code

Error Message

để người vận hành xác định chính xác dòng dữ liệu bị lỗi.

13. Settings

Lưu trong

settings.json

Bao gồm:

Provider

Ferry

Delay

Retry

Headless

Theme

Không hardcode trong chương trình.

14. Build

Chỉ build dạng

Portable EXE

Không tạo Installer.

15. Auto Update

Phần mềm được thiết kế để hỗ trợ

Auto Update

Chức năng có thể triển khai ở Sprint sau.

16. Coding Rules
GUI không chứa Business Logic.
Mọi Provider dùng chung Interface.
Worker Thread cho mọi tác vụ dài.
Không Hardcode.
Không Magic Number.
Không except: pass.
Không thay đổi Interface khi chưa thống nhất.
17. Quy trình Sprint

Mỗi Sprint gồm:

Thiết kế
Chốt thiết kế
Lập trình
Kiểm thử
Sửa lỗi
Khóa Sprint
Sprint tiếp theo
18. Quy tắc bàn giao

Mỗi Sprint phải có:

Mục tiêu
File thêm mới
File sửa
Code hoàn chỉnh từng file
Checklist kiểm thử
Kết quả mong đợi

Không gửi các đoạn mã rời để người dùng tự ghép.

19. Definition of Done

Một Sprint chỉ được xem là hoàn thành khi:

Build thành công.
Chạy không lỗi.
Đạt toàn bộ Checklist.
Người dùng xác nhận:

"Không có lỗi, tiếp tục sprint kế tiếp."

20. Nguyên tắc bảo toàn dữ liệu

DistanceCalculatorPro không bao giờ được phép làm mất dữ liệu của người dùng.

Nguyên tắc:

Chỉ ghi vào các cột Output.
Không ghi đè dữ liệu gốc.
Tự động lưu định kỳ theo thiết lập.
Khi chương trình dừng bất thường, người dùng có thể Resume.
Mọi thao tác ghi phải ưu tiên an toàn dữ liệu hơn tốc độ.
21. Quy tắc phát triển dự án
Thiết kế trước, lập trình sau.
Chỉ bắt đầu viết code khi người dùng ra lệnh:

"Chốt thiết kế"

Sau khi chốt:

Kiến trúc của Sprint được đóng băng.
Chỉ sửa Bug.
Không Refactor nếu không cần thiết.
Không thay đổi Interface.
Không đổi tên Class.
Không đổi cấu trúc thư mục.

Ý tưởng mới sẽ được đưa vào Product Backlog và xem xét ở Sprint hoặc phiên bản tiếp theo.

22. Mục tiêu chất lượng

DistanceCalculatorPro phải đạt các tiêu chí sau:

Ổn định.
Dễ mở rộng.
Dễ bảo trì.
Dễ kiểm thử.
Không phụ thuộc Provider.
Không phụ thuộc cấu trúc GUI.
Có thể mở rộng thêm nhiều Provider mà không phải viết lại hệ thống.
Trạng thái tài liệu

Software Specification v1.0 (Draft)

Đây được xem là tài liệu thiết kế nền tảng của dự án. Sau khi bạn xác nhận "Chốt thiết kế", tài liệu này sẽ được xem là đặc tả chính thức (Baseline Specification). Mọi Sprint lập trình sau đó sẽ tuân thủ tài liệu này và chỉ thay đổi khi có yêu cầu mới hoặc phát hiện vấn đề cần sửa trong quá trình phát triển.

23. Compatibility Matrix

Mỗi module trong dự án phải được theo dõi bằng một bảng tương thích.

Ví dụ:

Module	Sprint tạo	Sprint sửa cuối	Phụ thuộc
DistanceResult	Sprint 1	Sprint 1	Provider, Service
ErrorCode	Sprint 1	Sprint 1	Toàn hệ thống
Settings	Sprint 1	Sprint 4	GUI
MainWindow	Sprint 2	Sprint 4	Controller
GoogleWebProvider	Sprint 6	Sprint 6	DistanceResult

Mục đích:

Biết chính xác module nào bị ảnh hưởng khi sửa đổi.
Hạn chế sửa dây chuyền.
Dễ bảo trì và nâng cấp.

24. Architecture Decision Record (ADR)

Mỗi quyết định kiến trúc quan trọng sẽ được lưu thành một tài liệu ngắn trong thư mục:

docs/adr/

Ví dụ:

ADR-001-Use-PySide6.md
ADR-002-Provider-Interface.md
ADR-003-DistanceResult-Standard.md
ADR-004-Resume-Strategy.md
ADR-005-Settings-JSON.md

Mỗi ADR chỉ khoảng 1 trang với cấu trúc:

Bối cảnh (Context): Vì sao cần quyết định này.
Quyết định (Decision): Chúng ta chọn giải pháp nào.
Hệ quả (Consequences): Ảnh hưởng tích cực và giới hạn.

Ví dụ:

ADR-003 – DistanceResult Standard

Context: Cần nhiều Provider cùng hoạt động.
Decision: Mọi Provider bắt buộc trả về DistanceResult.
Consequences: GUI và Service không phụ thuộc Provider cụ thể.

Sau này nếu có người khác tham gia dự án, họ sẽ hiểu ngay lý do của các quyết định mà không cần đọc toàn bộ lịch sử trao đổi.

25. Module Contract (Frozen)

Mỗi module trong hệ thống bắt buộc phải có một "Module Contract", bao gồm:

Mục đích (Purpose)
Trách nhiệm (Responsibilities)
Đầu vào (Inputs)
Đầu ra (Outputs)
Phụ thuộc được phép (Allowed Dependencies)
Những điều bị cấm (Forbidden Responsibilities)

Ví dụ:

GoogleWebProvider

Purpose

Thu thập dữ liệu định tuyến từ Google Web.

Inputs

OriginLat
OriginLng
DestinationLat
DestinationLng
Routing Options

Outputs

DistanceResult

Allowed Dependencies

BrowserManager
Provider Interface

Forbidden

Không đọc/Ghi Excel.
Không cập nhật GUI.
Không đọc settings.json trực tiếp.
Không ghi log giao diện.

26. Integration Principles

Đây sẽ là bộ nguyên tắc bắt buộc khi tích hợp các module đã có.

Ví dụ:

GUI chỉ giao tiếp với Controller.
Controller không chứa Business Logic.
Service là nơi điều phối nghiệp vụ.
Provider chỉ lấy dữ liệu từ nguồn bên ngoài.
Engine chỉ xử lý tự động hóa trình duyệt.
Parser chỉ chuyển đổi dữ liệu thô thành Model.
Model không phụ thuộc GUI, Provider hay Service.
Mọi module phải có thể kiểm thử độc lập (nếu khả thi).