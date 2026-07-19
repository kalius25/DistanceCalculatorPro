Module Responsibility Specification (MRS) v1.0

Một module chỉ có một trách nhiệm duy nhất.

Tài liệu này giúp sau này khi review, chúng ta không còn tranh luận "đoạn code này nên để ở đâu".

1. GUI Layer
Chịu trách nhiệm
Hiển thị giao diện
Hiển thị Route
Progress Bar
Input Box
Button
Table
Status
Không được phép

❌ Parse HTML

❌ Convert đơn vị

❌ Retry

❌ Playwright

❌ Network

2. Controller Layer
Chịu trách nhiệm
Nhận Event từ GUI
Validate Input cơ bản
Tạo RouteRequest
Gọi Service
Cập nhật GUI
Không được phép

❌ Parse

❌ Build URL

❌ Playwright

❌ HTML

3. Service Layer
Chịu trách nhiệm
Điều phối nghiệp vụ
Chọn Provider
Xử lý Workflow
Trả RouteResult

Ví dụ

Calculate Distance

↓

Provider

↓

Result

Không quan tâm Google hoạt động thế nào.

4. Provider Layer

Ví dụ

GoogleMapsProvider
Chịu trách nhiệm
Gọi Engine
Trả RouteResult

Không parse.

Không convert.

5. Engine Layer
Chịu trách nhiệm

Browser Automation.

Ví dụ

Start Browser

↓

Open Google Maps

↓

Input Address

↓

Click Route

↓

Wait

↓

Get HTML

Không đọc HTML.

6. Parser Layer
Chịu trách nhiệm

Đọc HTML.

Ví dụ

HTML

↓

Find Route Card

↓

Distance Text

↓

Duration Text

↓

Summary

↓

RouteOption

Không convert.

7. Converter Layer

Ví dụ

15 mi

↓

24.14016

Ví dụ

1 hr 30 min

↓

90

Không HTML.

Không Regex ngoài conversion.

Không Logging.

8. Model Layer

Ví dụ

RouteOption

RouteResult

RouteRequest

Chỉ Data.

Không Method nghiệp vụ.

9. Enum Layer

Ví dụ

TravelMode

ProviderType

Không Function.

10. Constant Layer

Ví dụ

_DISTANCE_PATTERN

_ROUTE_SELECTOR

_HIGHWAY_KEYWORDS

Không Config.

Luồng dữ liệu chuẩn
User
 │
 ▼
GUI
 │
 ▼
Controller
 │
 ▼
RouteRequest
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
Google Maps
 │
 ▼
HTML
 │
 ▼
Parser
 │
 ▼
Converter
 │
 ▼
RouteOption
 │
 ▼
RouteResult
 │
 ▼
GUI
Quy tắc "đặt đúng chỗ"

Tôi muốn bổ sung một quy tắc mới vì nó sẽ giúp dự án ổn định hơn.

MRS-001: The Right Place Rule

Nếu một đoạn code có thể đặt ở nhiều nơi, hãy chọn nơi có trách nhiệm tự nhiên nhất.

Ví dụ:

Sai
Parser

↓

distance_to_km()

vì Parser không có trách nhiệm chuyển đổi đơn vị.

Đúng
Parser

↓

TextConverter.distance_to_km()

Một ví dụ khác:

Sai
GUI

↓

GoogleMapsEngine()

GUI không nên biết Playwright.

Đúng
GUI

↓

Controller

↓

Service

↓

Provider
MRS-002: One Knowledge Rule

Mỗi loại kiến thức chỉ tồn tại ở một nơi duy nhất.

Ví dụ:

Kiến thức	Nơi duy nhất
URL Google Maps	UrlBuilder
CSS Selector	Locator
Regex khoảng cách	TextConverter
Runtime Config	config.py
TravelMode	Enum
Route data	Models

Nhờ đó, khi Google Maps thay đổi selector, bạn chỉ cần sửa Locator, thay vì dò hàng chục file.

Sau MRS sẽ còn gì?

Theo tôi, sau khi hoàn thiện MRS, bộ tài liệu nền tảng của dự án đã đủ để bắt đầu phát triển lâu dài:

✅ Project Constitution (PC)
✅ Architecture Specification (AS)
✅ Module Responsibility Specification (MRS)
✅ Coding Standard (CS)
✅ Design Decision Document (DDD)
✅ Naming Convention (NC)

Đây sẽ là Baseline v1.0 của DistanceCalculatorPro.