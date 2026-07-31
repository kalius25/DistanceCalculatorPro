# DistanceCalculatorPro Roadmap

## Công nghệ giao diện

Framework được chọn:

**PySide6 (Qt for Python)**

Lý do lựa chọn:

* Giao diện hiện đại và chuyên nghiệp.
* Phù hợp ứng dụng desktop Windows.
* Hỗ trợ bảng dữ liệu lớn.
* Có hệ thống signal/slot tốt cho xử lý nền.
* Hỗ trợ theme sáng và tối.
* Có thể dùng Qt Designer.
* License phù hợp hơn PyQt6 nếu phát triển thương mại.
* Dễ mở rộng thành ứng dụng logistics chuyên sâu.

---

# Tổng quan Roadmap

```text
v1.0  Foundation                    ✔ Hoàn thành
v1.1  Engineering                   ✔ Hoàn thành
v1.2  Modern UI                     ← Giai đoạn hiện tại
v1.3  Productivity
v1.4  Accuracy
v1.5  Performance
v1.6  Multi Provider
v1.7  Power User
v1.8  Logistics Intelligence
v2.0  Enterprise
```

---

# v1.0 — Foundation ✔

## Kiến trúc

* Dependency Injection.
* Layered Architecture.
* SOLID ở mức phù hợp.
* Controller, Service, Provider và Engine được tách rõ.
* Không tạo dependency bên trong business class.
* Không để business logic phụ thuộc trực tiếp vào Qt, Excel hoặc Selenium.

## Chất lượng

* Unit test đầy đủ.
* Statement coverage 100%.
* Branch coverage 100%.
* Architecture Freeze.

## Tài liệu

* `README.md`
* `ARCHITECTURE.md`
* `ARCHITECTURE_DECISIONS.md`
* `CODING_STANDARD.md`
* `TESTING_GUIDELINES.md`

---

# v1.1 — Engineering ✔

Đã hoàn thành và không cần đưa vào kế hoạch triển khai tiếp theo.

Bao gồm các hạng mục như:

* CI/CD.
* Ruff.
* Black.
* Mypy.
* Pre-commit.
* Pytest.
* Coverage gate.
* Build và kiểm tra tự động.
* Chuẩn commit và release.

---

# v1.2 — Modern UI

**Sprint 1C.1 — Provider Configuration Workspace ✔**


Đây là giai đoạn hiện tại.

Mục tiêu là xây dựng giao diện người dùng hoàn chỉnh bằng PySide6 mà không làm thay đổi business layer hiện có.

---

## UI v1 — Batch Distance Calculator

### Mục tiêu

Cho phép người dùng:

1. Chọn file Excel.
2. Chọn sheet dữ liệu.
3. Chọn các cột đầu vào và đầu ra.
4. Thiết lập điều kiện tính tuyến đường.
5. Xem trước dữ liệu.
6. Chạy tính khoảng cách hàng loạt.
7. Theo dõi tiến độ.
8. Xem các dòng thành công và thất bại.
9. Lưu kết quả trở lại Excel.

---

## Bố cục UI v1

```text
┌──────────────────────────────────────────────────────────────────────┐
│ DistanceCalculatorPro                                      _ □ ×   │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  FILE EXCEL                                                          │
│                                                                      │
│  File:   [ D:\Data\Danh_sach_dia_chi.xlsx              ] [Browse]   │
│                                                                      │
│  Sheet:  [ Data                                           ▼ ]       │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  COLUMN MAPPING                                                      │
│                                                                      │
│  Origin Column:       [ Điểm đi                         ▼ ]          │
│  Destination Column:  [ Điểm đến                        ▼ ]          │
│                                                                      │
│  Distance Column:     [ Khoảng cách                     ▼ ]          │
│  Duration Column:     [ Thời gian                       ▼ ]          │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ROUTE SETTINGS                                                      │
│                                                                      │
│  Provider:            [ Google                          ▼ ]          │
│  Travel Mode:         [ Driving                         ▼ ]          │
│                                                                      │
│  Route Options:                                                     │
│                                                                      │
│  [✓] Alternative Routes                                             │
│  [ ] Avoid Tolls                                                     │
│  [ ] Avoid Highways                                                  │
│  [ ] Avoid Ferry                                                     │
│                                                                      │
│  Language:            [ Vietnamese                      ▼ ]          │
│  Region:              [ Vietnam                         ▼ ]          │
│  Timeout:             [ 30 ] seconds                                  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  DATA PREVIEW                                                        │
│                                                                      │
│  ┌─────┬──────────────────────┬──────────────────────┬────────────┐  │
│  │ Row │ Origin               │ Destination          │ Status     │  │
│  ├─────┼──────────────────────┼──────────────────────┼────────────┤  │
│  │  2  │ Cần Thơ              │ Cà Mau               │ Ready      │  │
│  │  3  │ Long Xuyên           │ Châu Đốc             │ Ready      │  │
│  │  4  │ Mỹ Tho               │ Bến Tre              │ Ready      │  │
│  └─────┴──────────────────────┴──────────────────────┴────────────┘  │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  PROGRESS                                                            │
│                                                                      │
│  ████████████████████░░░░░░░░░░░░  63%                             │
│                                                                      │
│  Processed: 630 / 1,000                                             │
│  Success:   622                                                      │
│  Failed:      8                                                      │
│  Elapsed:   00:08:32                                                 │
│  ETA:       00:05:05                                                 │
│                                                                      │
│           [ Start ]   [ Pause ]   [ Stop ]   [ Retry Failed ]       │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ACTIVITY LOG                                                        │
│                                                                      │
│  23:10:12  Started calculation                                      │
│  23:10:14  Row 2 completed — 174.5 km                               │
│  23:10:17  Row 3 completed — 58.2 km                                │
│  23:10:20  Row 4 failed — Route not found                           │
│                                                                      │
├──────────────────────────────────────────────────────────────────────┤
│  Ready                                           Version 1.2.0       │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Route Settings của UI v1

### Provider

Phiên bản đầu tiên:

```text
Google
```

Sau này mở rộng:

```text
Google
Bing
HERE
Mapbox
OSRM
OpenRouteService
```

### Travel Mode

```text
Driving
Walking
Bicycling
Transit
```

Chỉ hiển thị những chế độ mà provider hiện tại hỗ trợ.

### Alternative Routes

Khi bật:

```text
Google có thể trả về nhiều tuyến đường.
```

Ứng dụng sẽ chọn tuyến phù hợp theo chính sách đã cấu hình.

Mặc định:

```text
Bật
```

### Avoid Tolls

Tránh đường có trạm thu phí khi provider hỗ trợ.

Mặc định:

```text
Tắt
```

### Avoid Highways

Hạn chế sử dụng đường cao tốc.

Mặc định:

```text
Tắt
```

### Avoid Ferry

Tránh tuyến đường có phà hoặc tàu chở phương tiện.

Mặc định:

```text
Tắt
```

Tính năng này đặc biệt hữu ích tại các khu vực miền Tây, nơi một số tuyến đề xuất có thể đi qua phà.

### Timeout

Thời gian tối đa cho mỗi yêu cầu.

Giá trị mặc định:

```text
30 giây
```

---

## Hành vi của Avoid Ferry

UI không trực tiếp xử lý logic tránh phà.

Luồng đúng:

```text
QCheckBox Avoid Ferry
        ↓
ViewModel / Presenter
        ↓
RouteRequest
        ↓
CalculationService
        ↓
Provider
        ↓
Engine / URL Builder
```

Ví dụ:

```python
request = RouteRequest(
    origin=origin,
    destination=destination,
    travel_mode=TravelMode.DRIVING,
    alternatives=True,
    toll_preference=RoutePreference.AVOID,
    highway_preference=RoutePreference.AUTO,
    ferry_preference=RoutePreference.AVOID,
)
```

Nếu model hiện tại chưa có:

```python
ferry_preference
```

thì bổ sung trường này vào `RouteRequest` trước khi nối vào UI.

Không xử lý bằng cách truyền trực tiếp `QCheckBox` xuống Service hoặc Provider.

---

## Thành phần kỹ thuật UI v1

```text
app/
├── presentation/
│   ├── main_window.py
│   ├── viewmodels/
│   │   └── calculation_viewmodel.py
│   ├── widgets/
│   │   ├── file_selector.py
│   │   ├── column_mapping_panel.py
│   │   ├── route_settings_panel.py
│   │   ├── preview_table.py
│   │   ├── progress_panel.py
│   │   └── log_panel.py
│   ├── dialogs/
│   │   ├── error_dialog.py
│   │   └── result_dialog.py
│   ├── workers/
│   │   └── calculation_worker.py
│   ├── themes/
│   │   ├── light.qss
│   │   └── dark.qss
│   └── resources/
│       ├── icons/
│       └── resources.qrc
│
├── controllers/
├── services/
├── providers/
├── engines/
├── models/
└── configuration/
```

---

## Luồng hoạt động UI v1

```text
Người dùng chọn file
        ↓
CalculationController.get_sheet_names()
        ↓
Người dùng chọn sheet
        ↓
CalculationController.get_preview()
        ↓
Người dùng chọn Column Mapping
        ↓
CalculationController.validate_mapping()
        ↓
CalculationController.build_requests()
        ↓
BatchCalculationService
        ↓
CalculationService
        ↓
Provider
        ↓
Engine
        ↓
Kết quả cập nhật lên UI
        ↓
Ghi lại Excel
```

---

## Xử lý nền

Tính khoảng cách không được chạy trực tiếp trên Qt Main Thread.

Phải sử dụng:

```text
QThread
hoặc
QThreadPool + QRunnable
```

Luồng:

```text
Main Thread
    ├── Giao diện
    ├── Nút bấm
    └── Hiển thị tiến độ

Worker Thread
    ├── Chạy batch
    ├── Gọi service
    └── Phát signal kết quả
```

Các signal đề xuất:

```python
progress_changed
row_completed
row_failed
status_changed
finished
cancelled
fatal_error
```

Không cập nhật widget trực tiếp từ worker thread.

---

## Phạm vi UI v1

UI v1 cần hoàn thành:

* Chọn file Excel.
* Chọn sheet.
* Chọn mapping cột.
* Chọn provider.
* Chọn travel mode.
* Alternative Routes.
* Avoid Tolls.
* Avoid Highways.
* Avoid Ferry.
* Chọn ngôn ngữ và vùng.
* Xem preview.
* Validate dữ liệu.
* Start.
* Pause.
* Stop an toàn.
* Progress.
* Số dòng thành công và thất bại.
* Activity log.
* Retry Failed.
* Ghi kết quả trở lại Excel.
* Thông báo hoàn tất.
* Thông báo lỗi dễ hiểu.

UI v1 chưa cần:

* Dashboard nhiều trang.
* Biểu đồ.
* Multi-provider comparison.
* Browser pool.
* Route optimization.
* Logistics Intelligence.
* Web API.
* Multi-user.

---

# v1.3 — Productivity

Sau khi UI v1 hoạt động ổn định.

## Hạng mục

* Retry các dòng lỗi.
* Resume phiên chạy bị gián đoạn.
* Pause và Continue.
* Graceful Cancel.
* Recent Files.
* Lưu Column Mapping.
* Lưu Route Settings.
* Lịch sử phiên chạy.
* Xuất danh sách dòng lỗi.
* Chạy lại từ checkpoint.
* Tự động lưu kết quả theo từng khoảng.

## Mục tiêu

Không để người dùng phải chạy lại toàn bộ file chỉ vì một số ít dòng lỗi hoặc ứng dụng bị gián đoạn.

---

# v1.4 — Accuracy

## Hạng mục

* Chuẩn hóa địa chỉ.
* Hỗ trợ tọa độ.
* Phát hiện địa chỉ thiếu tỉnh hoặc quốc gia.
* Phát hiện kết quả 0 km.
* Phát hiện thời gian bất thường.
* Outlier detection.
* Duplicate detection.
* Đánh dấu tuyến có phà.
* Đánh dấu tuyến có thu phí.
* Đánh dấu tuyến đi cao tốc.
* So sánh tính hợp lý giữa khoảng cách và thời gian.
* Cảnh báo địa chỉ có nhiều kết quả gần giống nhau.

## Mục tiêu

Tăng độ tin cậy của dữ liệu đầu ra, không chỉ tính được kết quả.

---

# v1.5 — Performance

## Hạng mục

* SQLite cache.
* Smart cache key.
* Browser warm-up.
* Batch scheduler.
* Tự động lưu checkpoint.
* Hạn chế mở lại cùng một trang.
* Kiểm soát memory khi chạy file lớn.
* Browser pool khi đã đánh giá độ ổn định.
* Điều chỉnh số worker theo cấu hình máy.

## Thứ tự ưu tiên

```text
1. Cache
2. Checkpoint
3. Browser warm-up
4. Batch scheduler
5. Browser pool
```

Không triển khai browser pool quá sớm vì có thể làm tăng:

* CAPTCHA.
* Rate limit.
* Mức sử dụng RAM.
* Lỗi đồng bộ.
* Độ phức tạp khi retry.

---

# v1.6 — Multi Provider

## Hạng mục

* Provider selector.
* Google Provider.
* OSRM Provider.
* OpenRouteService Provider.
* HERE Provider.
* Bing Provider.
* Mapbox Provider.
* Provider fallback.
* Provider priority.
* Provider health check.
* So sánh kết quả giữa các provider.

## Ví dụ fallback

```text
Google
   ↓ lỗi
OSRM
   ↓ lỗi
HERE
```

## Nguyên tắc

Business layer chỉ phụ thuộc vào:

```python
BaseProvider
```

Không sửa `CalculationService` mỗi khi thêm provider mới.

---

# v1.7 — Power User

## Hạng mục

* Column Mapping Template.
* Route Setting Profile.
* Command Line Interface.
* Chạy không cần mở GUI.
* Auto Export.
* CSV và JSON.
* Scheduled Run.
* Import profile.
* Export profile.
* Cấu hình bằng file.
* Chế độ chạy im lặng.
* Log kỹ thuật riêng.
* Batch nhiều file.

## Ví dụ CLI

```bash
distance-calculator \
    --input data.xlsx \
    --sheet Data \
    --provider google \
    --travel-mode driving \
    --avoid-ferry \
    --output result.xlsx
```

---

# v1.8 — Logistics Intelligence

Đây là hướng phát triển tạo khác biệt lớn nhất cho sản phẩm.

## Distance Matrix

```text
50 địa điểm
    ↓
Ma trận 50 × 50
```

Ứng dụng:

* So sánh kho.
* Chọn hub.
* Phân vùng giao hàng.
* Phân tích mạng lưới.

## Warehouse Assignment

Với một điểm giao hàng mới:

```text
Kho Cần Thơ       92 km
Kho Long Xuyên   128 km
Kho Tiền Giang   161 km
```

Hệ thống đề xuất kho phù hợp nhất.

## Delivery Territory

Tạo vùng phục vụ theo:

* Khoảng cách.
* Thời gian giao.
* Bán kính.
* Tỉnh.
* Cụm địa lý.

## Clustering

Tự nhóm điểm giao thành các cụm phù hợp.

## Route Optimization

Đầu vào:

```text
150 điểm giao
20 xe
Tải trọng từng xe
Khung giờ giao
Kho xuất phát
```

Đầu ra:

```text
Danh sách tuyến
Thứ tự điểm giao
Tổng km
Tổng thời gian
Tải trọng sử dụng
```

## Cost Model

Tính chi phí dự kiến theo:

* Số km.
* Thời gian.
* Tải trọng xe.
* Phí cầu đường.
* Phà.
* Nhiên liệu.
* Lương tài xế.
* Chi phí thuê xe.

---

# v2.0 — Enterprise

Chỉ triển khai khi có nhu cầu nhiều người dùng hoặc vận hành tập trung.

## Hạng mục

* REST API.
* Web UI.
* Multi-user.
* Authentication.
* Authorization.
* Audit Log.
* PostgreSQL.
* Docker.
* Centralized configuration.
* Centralized logging.
* Monitoring.
* Worker queue.
* Distributed calculation.
* Quản lý quota.
* Quản lý API key.
* Báo cáo quản trị.
* Triển khai trên máy chủ nội bộ hoặc cloud.

---

# Thứ tự triển khai đề xuất

```text
Bước 1
UI v1 bằng PySide6

Bước 2
Worker thread và progress

Bước 3
Pause, Stop và Retry Failed

Bước 4
Checkpoint và Resume

Bước 5
SQLite Cache

Bước 6
Accuracy Validation

Bước 7
Multi Provider

Bước 8
Power User

Bước 9
Logistics Intelligence

Bước 10
Enterprise khi có nhu cầu thực tế
```

---

# Mốc phát hành đề xuất

```text
v1.2.0
UI v1 chạy được toàn bộ quy trình Excel → Calculate → Save

v1.2.1
Sửa lỗi và hoàn thiện trải nghiệm

v1.3.0
Retry, Pause, Resume và History

v1.4.0
Accuracy và Address Validation

v1.5.0
Cache và tối ưu hiệu năng

v1.6.0
Multi Provider

v1.7.0
CLI và Power User

v1.8.0
Logistics Intelligence

v2.0.0
Enterprise Platform
```

---

# Tiêu chí hoàn thành UI v1

UI v1 chỉ được xem là hoàn thành khi:

* Mở được file Excel hợp lệ.
* Hiển thị được danh sách sheet.
* Hiển thị được header và preview.
* Mapping cột hoạt động chính xác.
* Route Settings bao gồm Avoid Ferry.
* Không block giao diện khi tính toán.
* Progress cập nhật chính xác.
* Stop không làm hỏng file.
* Retry Failed hoạt động.
* Kết quả được ghi đúng cột.
* Lỗi được hiển thị dễ hiểu.
* Không đưa business logic vào Qt widget.
* Unit test và coverage tiếp tục đạt chuẩn.
* Có thể build thành ứng dụng Windows độc lập.
