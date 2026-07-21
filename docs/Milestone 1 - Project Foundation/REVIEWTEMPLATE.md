DistanceCalculatorPro Review Template v1.0

Mỗi file sẽ được review theo đúng mẫu dưới đây.

1. Module Information
Module:
google_maps_parser.py

Layer:
Parser

Status:
Review
2. Responsibility Review

Ví dụ

✅ Đúng

Parse Route Card
Parse Distance
Parse Duration

❌ Không nên

Retry
Logging
Convert Unit
Business Logic
3. Architecture Review

Kiểm tra

Có đúng Layer không?
Có gọi sai Layer không?
Có Circular Dependency không?

Kết quả

PASS

hoặc

FAIL
4. Coding Standard Review

Theo đúng CS

Ví dụ

Rule	Result
Hardcode	PASS
Config	PASS
Enum	PASS
Constant	PASS
Logging	PASS
Exception	PASS
Type Hint	PASS
Docstring	PASS
5. Design Decision Review

Kiểm tra DDD

Ví dụ

DDD	Result
Parser only Parse	PASS
Canonical Unit	PASS
Locator Pattern	PASS
6. Issues

Phân loại

🔴 Critical

🟠 Recommended

🟡 Optional

🟢 Future

Ví dụ

🟠 Recommended

Regex nên chuyển thành Internal Constant.
7. Refactor Plan

Ví dụ

1.
Move regex

2.
Replace selector

3.
Add type hint

4.
Add docstring
8. Freeze Checklist
Item	Status
Compile	✅
Architecture	✅
Responsibility	✅
Coding Standard	✅
DDD	✅
Type Hint	✅
Docstring	✅
Unit Test	✅

Nếu tất cả đều đạt:

Module Status

✅ FREEZE
Quy tắc review mới

Để tránh "review lan man", mỗi lần chỉ xử lý 01 module.

Ví dụ:

Sprint 2

text_converter.py

Chỉ review file đó.

Không nhảy sang Engine.

Không nhảy sang GUI.

Nếu phát hiện vấn đề liên quan module khác, chỉ ghi chú:

Future Review