v0.5
✅ BaseProvider
✅ GoogleWebProvider
✅ GoogleRoutesProvider
✅ GoogleMapsEngine
✅ Controller gọi Provider
v0.6
✅ Playwright
✅ Tự động mở Google Maps
✅ Đọc Distance
✅ Đọc Duration
v0.7
✅ Ghi Excel
✅ Progress
✅ Cancel
v0.8
✅ SQLite Cache
✅ Retry
✅ Resume
v1.0
✅ Build .exe
✅ Installer
✅ Settings
✅ Auto Update (nếu cần)


Sprint 1.4.1 – Refactor đồng bộ

DistanceCalculatorPro v1.0 Architecture
Package 1 – Core Foundation (~8 file)
Enums
Constants
Models
Package 2 – Infrastructure (~6 file)
Exceptions
Logger
BrowserManager
GoogleMapsUrlBuilder
Package 3 – Engine (~5 file)
GoogleMapsEngine
Parser V3
Package 4 – Business (~4 file)
Providers
Services
Package 5 – Tests (~5 file)
Toàn bộ test
Regression test
Debug tools
Package 6 – Excel & GUI
Tích hợp import/export Excel
Kết nối giao diện

Package 1 - Foundation
app/
│
├── enums/
│      __init__.py
│      travel_mode.py
│      route_preference.py
│      provider_type.py
│
├── constants/
│      __init__.py
│      google_maps.py
│
└── models/
       route_request.py
       route_option.py
       route_result.py

Package 1A
app/enums/
    __init__.py
    travel_mode.py
    route_preference.py
    provider_type.py
Package 1B
app/constants/
    google_maps.py
Package 1C
app/models/
    route_request.py
    route_option.py
    route_result.py

Release 1
Core Foundation
Enums
Models
Constants
Exceptions
Release 2
Engine
BrowserManager
UrlBuilder
Engine
Parser V3
Release 3
Business Layer
Provider
Services
Batch
Release 4
Tests
Unit Test
Regression Test
Debug
Release 5
Excel
Import
Export
Batch
Release 6
GUI
PySide6
Progress
Cancel
Log