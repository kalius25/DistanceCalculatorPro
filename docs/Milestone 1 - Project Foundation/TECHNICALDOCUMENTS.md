📚 DistanceCalculatorPro Technical Documents
1. Coding Standard (CS) ✅

Mục đích: Quy định cách viết code.

Bao gồm:

Architecture Rules
Configuration Rules
Locator Rules
Parser Rules
Converter Rules
Data Rules
Enum Rules
Constant Rules
Code Rules
Logging & Exception Rules
Future Extension Rules

Đây là tài liệu để trả lời câu hỏi "Code phải viết như thế nào?"

2. Design Decision Document (DDD) ✅

Mục đích: Lưu lại các quyết định kiến trúc.

Ví dụ:

Vì sao dùng Layered Architecture
Vì sao Parser không Convert
Vì sao Canonical Unit là Kilometer
Vì sao Locator tách riêng
Vì sao giữ backward compatibility

Đây là tài liệu trả lời câu hỏi "Tại sao lại thiết kế như vậy?"

3. Project Architecture (PA) ✅

Đây là tài liệu chúng ta sẽ viết tiếp.

Ví dụ:

DistanceCalculatorPro
│
├── gui/
│
├── controller/
│
├── service/
│
├── provider/
│
│   └── google_maps/
│
├── engine/
│
├── parser/
│
├── converter/
│
├── locator/
│
├── models/
│
├── enums/
│
├── utils/
│
└── config.py

Mô tả trách nhiệm từng thư mục.

4. Module Responsibility (MR) ✅

Ví dụ

GoogleMapsEngine

Responsible:

Open Browser
Navigate
Wait
Call Parser

Not Responsible:

Parse HTML
Convert Data
Business Logic
GoogleMapsParser

Responsible:

Parse HTML

Not Responsible:

Retry
Logging
Convert
Browser

Đây sẽ là tài liệu cực kỳ hữu ích sau này.

5. Data Model Specification (DMS) ✅

Ví dụ

RouteOption
distance_text: str
distance_km: float
duration_text: str
duration_minutes: int
summary: str
warnings: list[str]
...

Ý nghĩa từng field.

Nguồn dữ liệu.

Ví dụ dữ liệu.

6. Error Handling Specification (EHS)

Ví dụ

Parser gặp lỗi

↓

return None

Engine

↓

Retry

↓

Provider

↓

RouteResult.error

Không được throw lung tung.

7. Unit Test Specification (UTS)

Ví dụ

TextConverter

Test

350 m
999 m
1 km
1,2 km
15 mi
500 ft
Parser

Test

0 route
1 route
nhiều route
không có toll
có ferry
locale EN
locale VI
8. Development Workflow (DW)

Ví dụ

Mỗi module phải review theo thứ tự:

Compile

↓

Logic

↓

Architecture

↓

SRP

↓

Hardcode

↓

Config

↓

Enum

↓

Logging

↓

Exception

↓

Performance

↓

Readability

↓

Unit Test

Không review ngược.

📌 Tôi muốn bổ sung thêm một nguyên tắc cuối cùng

Đây là nguyên tắc tôi đánh giá là quan trọng nhất đối với dự án này.

DDD-020. Evolution Before Expansion

Chỉ mở rộng tính năng sau khi kiến trúc hiện tại đã ổn định và được "freeze".

Ví dụ:

❌ Không nên làm ngay:

HERE Maps
Bing Maps
Mapbox
API Mode
Async
Multi Thread
Plugin

Khi Google Maps Web còn chưa ổn định.

Đúng nên là:

Google Maps Web
        │
        ▼
Ổn định

Freeze

100% Unit Test

↓

Mở rộng Provider

Đây là nguyên tắc giúp dự án tránh tình trạng "thêm tính năng liên tục nhưng nền móng chưa vững".