Hiến pháp dự án (Project Constitution)

Kể từ thời điểm này, chúng ta làm việc theo các nguyên tắc sau:

1. Thiết kế trước, lập trình sau
Chỉ thảo luận kiến trúc, GUI, workflow, interface, quy tắc.
Chỉ khi bạn nói "Chốt thiết kế" thì mới bắt đầu viết code.
2. Phát triển theo Sprint

Mỗi Sprint phải có:

Mục tiêu
Phạm vi
File thêm mới
File sửa
Code hoàn chỉnh
Checklist kiểm thử
Kết quả mong đợi

Không gộp nhiều Sprint vào một lần bàn giao.

3. Bàn giao bằng file hoàn chỉnh

Mặc định tôi sẽ gửi:

Toàn bộ nội dung của từng file được thay đổi.
Không gửi các đoạn code rời để bạn tự ghép (trừ khi bạn yêu cầu patch).
4. Sau khi bạn chạy thử

Chỉ có hai trạng thái:

A. Có lỗi

Bạn báo lỗi hoặc gửi ảnh lỗi.

↓

Tôi chỉ sửa các file liên quan.

↓

Không chuyển Sprint.

B. Bạn xác nhận

Không có lỗi, tiếp tục sprint kế tiếp

↓

Sprint được khóa.

↓

Chuyển Sprint mới.

5. Sprint đã khóa sẽ không thay đổi

Sau khi hoàn thành:

Không refactor.
Không đổi tên class.
Không đổi cấu trúc thư mục.
Không đổi interface.

Chỉ sửa nếu:

Có bug.
Có yêu cầu mới.
6. Không đoán yêu cầu

Nếu thiếu thông tin làm ảnh hưởng đến kiến trúc:

→ Tôi sẽ hỏi.

Nếu chỉ là chi tiết triển khai:

→ Tôi tự quyết theo các quy tắc đã thống nhất.

7. Không phá vỡ chức năng cũ

Mọi Sprint mới phải tương thích với Sprint trước.

Đây là nguyên tắc bắt buộc.

8. Luôn ưu tiên khả năng mở rộng

Mọi thiết kế đều phải hướng tới:

Google Web
Google Routes API
HERE
OSRM
Mapbox
GraphHopper
Provider mới trong tương lai

mà không phải viết lại GUI.

9. Luôn giữ chất lượng ở mức "sản phẩm"

Mục tiêu không phải là "code chạy được", mà là:

Dễ đọc.
Dễ bảo trì.
Dễ mở rộng.
Dễ debug.
Có thể phát triển trong nhiều năm.
Một quy tắc tôi xin bổ sung

Đây là quy tắc duy nhất tôi muốn thêm vì nó sẽ tiết kiệm rất nhiều thời gian cho cả hai.

Quy tắc "Thiết kế chỉ tiến lên"

Trong giai đoạn thiết kế:

Chúng ta được phép bổ sung.
Được phép cải tiến.
Được phép thay đổi.

Nhưng sau khi bạn nói:

Chốt thiết kế

thì Sprint đó được xem là đóng băng (Design Freeze).

Nếu sau này xuất hiện ý tưởng hay hơn, tôi sẽ:

Không tự ý thay đổi Sprint hiện tại.
Ghi nhận nó vào Backlog để áp dụng ở Sprint hoặc phiên bản sau.

Ví dụ:

"Ý tưởng này rất hay, nhưng sẽ ảnh hưởng kiến trúc của Sprint 2. Tôi đề xuất đưa vào Backlog cho Sprint 6."

Cách làm này giúp dự án tiến đều, tránh việc cứ quay lại sửa những phần đã ổn định.

Cam kết của tôi

Trong quá trình đồng hành cùng dự án này, tôi sẽ coi DistanceCalculatorPro là một sản phẩm phần mềm thực sự, không phải là một ví dụ minh họa. Mọi đề xuất sẽ ưu tiên:

Tính ổn định.
Khả năng mở rộng.
Trải nghiệm người dùng.
Khả năng bảo trì lâu dài.

Khi bạn sẵn sàng, chúng ta sẽ tiếp tục hoàn thiện phần thiết kế còn lại. Đến khi bạn nói "Chốt thiết kế", tôi sẽ bắt đầu Sprint đầu tiên theo đúng quy trình mà chúng ta đã thống nhất.

10. Quy tắc bàn giao Sprint (bổ sung)

Nếu tổng dung lượng mã nguồn của một Sprint vượt quá giới hạn phản hồi của ChatGPT:

Một Sprint được phép chia thành nhiều Part.
Mỗi Part phải chứa file hoàn chỉnh, không cắt giữa file.
Chỉ khi bàn giao xong Part cuối cùng, bạn mới copy toàn bộ vào project để kiểm thử.
Sau khi bạn xác nhận "Không có lỗi, tiếp tục sprint kế tiếp.", Sprint mới được khóa.

Như vậy vẫn giữ đúng nguyên tắc không có file bị cắt và không phải tự ghép mã.