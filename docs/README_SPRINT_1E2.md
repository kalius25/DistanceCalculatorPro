# Sprint 1E.2 — Developer Diagnostics Framework

## Mục tiêu

Cung cấp chẩn đoán có thể bật/tắt khi Google Maps thay đổi giao diện hoặc parser
không lấy đủ dữ liệu, nhưng không làm nặng chế độ sử dụng thông thường.

## Bật và tắt

Mở menu **Debug** trong ứng dụng:

1. Bật **Debug Mode**.
2. Chọn **Trace Browser** để log URL và số route card.
3. Chọn **Parser Diagnostics** để log từng route đã parse.
4. Tùy chọn **Save HTML**, **Save Screenshot**, **Save Parser JSON**.

Các lựa chọn được lưu bằng `QSettings` và được khôi phục ở lần chạy sau.
Tắt **Debug Mode** để ngừng toàn bộ diagnostic logging và artifact capture.

## Artifact

Mặc định artifact được lưu tại:

```text
logs/debug/html
logs/debug/screenshots
logs/debug/json
```

JSON chứa số route card, số route parse thành công và các trường quan trọng của
từng route: summary, distance, duration, toll, ferry và highway.

## Release behavior

Khi Debug Mode tắt:

- Không ghi browser trace.
- Không ghi parser diagnostic.
- Không tạo HTML, screenshot hoặc JSON.
- Logger trở về level được cấu hình trong application config.
