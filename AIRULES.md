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