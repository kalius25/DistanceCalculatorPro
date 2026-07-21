Module Contract v1.0 (Frozen)

Đây là Module Contract mà tôi đang ghi nhận cho DistanceCalculatorPro.

1. GUI Layer
Purpose

Hiển thị giao diện và tương tác với người dùng.

Responsibilities
Hiển thị dữ liệu.
Thu nhận thao tác người dùng.
Điều hướng sự kiện.
Inputs
User Action
Controller Response
Outputs
Request cho Controller
Allowed Dependencies
Controllers
Forbidden
Không gọi Provider.
Không mở Browser.
Không đọc Excel.
Không parse HTML.
Không xử lý Business Logic.
2. Controller Layer
Purpose

Điều phối luồng xử lý.

Responsibilities
Nhận yêu cầu từ GUI.
Gọi Service.
Trả kết quả về GUI.
Inputs
GUI Request
Outputs
Service Request
ViewModel
Allowed Dependencies
Services
Models
Forbidden
Không dùng Playwright.
Không parse HTML.
Không thao tác Excel.
Không truy cập Google trực tiếp.
3. Service Layer
Purpose

Business Logic của hệ thống.

Responsibilities
Điều phối quy trình.
Gọi Provider.
Gọi Excel Service.
Logging.
Inputs
RouteRequest
User Settings
Outputs
RouteResult
Status
Allowed Dependencies
Providers
Models
Excel Service
Logger
Forbidden
Không thao tác DOM.
Không cập nhật GUI.
Không điều khiển Browser.
4. Provider Layer
Purpose

Lấy dữ liệu từ nguồn bên ngoài.

Responsibilities
Gọi Engine.
Chuyển dữ liệu về Model.
Inputs
RouteRequest
Outputs
DistanceResult
Allowed Dependencies
Engines
Parsers
Models
Forbidden
Không đọc/Ghi Excel.
Không cập nhật GUI.
Không đọc Settings trực tiếp.
Không chứa Business Workflow.
5. Engine Layer
Purpose

Browser Automation.

Responsibilities
Playwright.
Navigation.
DOM.
Retry thấp tầng.
Inputs
URL
Browser Command
Outputs
HTML
DOM
Allowed Dependencies
Playwright
Utils
Forbidden
Không parse Business Data.
Không ghi Excel.
Không biết GUI.
Không biết Business Logic.
6. Parser Layer
Purpose

HTML → Model.

Responsibilities
Parse dữ liệu.
Validate.
Inputs
HTML
DOM
Outputs
RouteResult
DistanceResult
Allowed Dependencies
Models
Forbidden
Không mở Browser.
Không ghi Log nghiệp vụ.
Không gọi Google.
Không xử lý Workflow.
7. Model Layer
Purpose

Trao đổi dữ liệu giữa các Layer.

Responsibilities
DTO.
Entity.
Immutable Data (nếu phù hợp).
Inputs
Data
Outputs
Data
Allowed Dependencies
Enum
Forbidden
Không có Business Logic.
Không gọi Service.
Không gọi Provider.
Không đọc Config.
8. Config Layer
Purpose

Quản lý cấu hình hệ thống.

Responsibilities
System Configuration.
Runtime Settings.
Version.
Inputs
JSON
Default Values
Outputs
Config Object
Allowed Dependencies
None
Forbidden
Không chứa Business Logic.
9. Utility Layer
Purpose

Các hàm dùng chung.

Responsibilities
Logging.
Converter.
Helper.
Allowed Dependencies
Standard Library
Forbidden
Không biết Business Logic.
10. Exception Layer
Purpose

Chuẩn hóa xử lý lỗi.

Responsibilities
Error Hierarchy.
Exception Mapping.
Outputs
ErrorCode
Exception
Forbidden
Không ghi Log.
Không xử lý GUI.