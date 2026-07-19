DistanceCalculatorPro Design Decisions (DDD) v1.0
DDD-001. Layered Architecture
Decision

Áp dụng kiến trúc phân tầng.

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
Reason
Phụ thuộc một chiều.
Dễ Unit Test.
Dễ thay Provider.
Giảm Coupling.
Status

✅ Freeze

DDD-002. URL Builder độc lập
Decision

Toàn bộ việc tạo URL Google Maps chỉ thực hiện trong:

GoogleMapsUrlBuilder
Reason

Không để Engine hoặc Provider tự nối URL.

Nếu Google thay đổi URL chỉ sửa một nơi.

Status

✅ Freeze

DDD-003. build_route() chỉ là Compatibility Wrapper
Decision

API mới:

build(RouteRequest)

API cũ:

build_route(...)

chỉ gọi sang API mới.

Reason

Không phá backward compatibility.

Status

✅ Freeze

DDD-004. Locator Pattern
Decision

Mọi CSS Selector chỉ tồn tại trong

GoogleMapsLocator
Reason

Google đổi DOM chỉ sửa một file.

Parser không biết Selector.

Status

✅ Freeze

DDD-005. Parser chỉ Parse
Decision

Parser chỉ lấy dữ liệu thô.

Ví dụ

350 m
2 giờ 15 phút
Parser không được
Convert
Retry
Log
Business Logic
Reason

Đúng nguyên tắc Single Responsibility.

Status

✅ Freeze

DDD-006. Converter chịu trách nhiệm chuẩn hóa
Decision

Mọi chuyển đổi dữ liệu đều nằm trong Converter.

Ví dụ

350 m

↓

0.35 km
Reason

Parser luôn đơn giản.

Mọi logic chuyển đổi tập trung.

Status

✅ Freeze

DDD-007. Canonical Storage Unit
Decision

Khoảng cách trong toàn bộ hệ thống luôn lưu bằng

Kilometer

Thông qua

distance_km
Reason
Sort
Compare
Filter
Export

đều dễ.

Status

✅ Freeze

DDD-008. Raw Text luôn được giữ
Decision

Model luôn lưu

distance_text

nguyên văn từ Google.

Ví dụ

350 m

hoặc

12.5 mi
Reason

GUI hiển thị đúng như Google.

Không bị mất thông tin.

Status

✅ Freeze

DDD-009. UI chỉ hiển thị
Decision

UI không convert dữ liệu.

UI chỉ hiển thị

distance_text

hoặc Formatter.

Reason

Không đưa Business Logic lên GUI.

Status

✅ Freeze

DDD-010. Formatter là tầng mở rộng
Decision

Nếu sau này hỗ trợ

km

mi

m

ft

thì tạo

DistanceFormatter

không sửa Parser.

Reason

Open/Closed Principle.

Status

🟡 Planned

DDD-011. Internal Constant
Decision

Regex

Keyword

Selector

không đưa Config.

Đặt đầu file.

Reason

Không làm config phình to.

Status

✅ Freeze

DDD-012. Config chỉ chứa Runtime Configuration
Decision

Config chỉ chứa

Timeout
Retry
Language
Region
Browser

Không chứa

Regex
Selector
Keyword
Status

✅ Freeze

DDD-013. Enum chỉ dùng cho Domain
Decision

Chỉ tạo Enum cho Domain.

Ví dụ

TravelMode

RoutePreference

ProviderType

Không tạo Enum cho

Regex

Keyword

Selector
Status

✅ Freeze

DDD-014. Backward Compatibility ưu tiên hơn Refactor
Decision

Trong quá trình refactor

Không đổi API nếu còn caller.

Reason

Giảm rủi ro.

Status

✅ Freeze

DDD-015. RouteOption là Domain Model
Decision

RouteOption chỉ lưu dữ liệu.

Không chứa logic.

Reason

Model không làm Business Logic.

Status

✅ Freeze

DDD-016. Converter phải hỗ trợ đa định dạng Google
Decision

Converter hỗ trợ

m

km

mi

ft

và nhiều locale.

Reason

Không phụ thuộc quốc gia.

Status

✅ Freeze

DDD-017. Google Provider không phụ thuộc GUI
Decision

Provider chỉ trả

RouteResult

GUI tự quyết định hiển thị.

Reason

Có thể dùng CLI

REST API

Batch

sau này.

Status

✅ Freeze

DDD-018. Một nguồn dữ liệu (Single Source of Truth)
Decision

Mỗi thông tin chỉ có một nơi chịu trách nhiệm.

Ví dụ:

Dữ liệu	Nguồn duy nhất
URL	GoogleMapsUrlBuilder
Selector	GoogleMapsLocator
Chuyển đổi đơn vị	TextConverter
Runtime Config	config.py
Route Model	RouteOption
Browser Automation	GoogleMapsEngine
Reason

Giảm trùng lặp và tránh mâu thuẫn khi bảo trì.

Status

✅ Freeze

DDD-019. Thứ tự ưu tiên khi Review Code
Decision

Mỗi module sẽ được review theo thứ tự:

Compile
Logic
Architecture
Single Responsibility
Hardcode
Config
Enum
Logging
Exception
Performance
Readability
Reason

Ưu tiên sửa lỗi ảnh hưởng đến tính đúng đắn trước, sau đó mới tối ưu chất lượng mã.

Status

✅ Freeze

DDD-020. Evolution Before Expansion

Chỉ mở rộng tính năng sau khi kiến trúc hiện tại đã ổn định và được "freeze".

Status

✅ Freeze


Roadmap (DDD)
Version	Trạng thái
DDD v1.0	✅ Freeze
DDD v1.1	Bổ sung Unit Test Strategy
DDD v1.2	Bổ sung Multi Provider (Google, HERE, Mapbox, Bing...)
DDD v2.0	Plugin Architecture
DDD v3.0	Async Provider & Parallel Route Query