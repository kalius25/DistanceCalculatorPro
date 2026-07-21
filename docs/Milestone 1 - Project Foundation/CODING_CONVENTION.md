Rule 1 — Không có Magic String

Ví dụ:

❌

locator.wait_for(
    state="visible",
)

✅

_WAIT_STATE = "visible"

locator.wait_for(
    state=_WAIT_STATE,
)
Rule 2 — Một helper chỉ làm một việc

Ví dụ

❌

_fill_route_input()

↓

wait

↓

fill

↓

press enter

↓

wait route

Helper này làm quá nhiều.

Đúng sẽ là:

_fill_route_input()

↓

_select_travel_mode()

↓

_wait_routes()
Rule 3 — Public API phải cực kỳ ngắn

Ví dụ

Engine chỉ có:

find_routes()

Parser chỉ có:

parse()

Provider sau này:

calculate()

Service:

calculate()

Controller:

calculate()

API càng nhỏ càng dễ bảo trì.

Rule 4 — Không để Playwright lan khắp project

Playwright chỉ nên xuất hiện trong:

engine/

Không được có:

page.locator(...)

ở

Provider
Service
Controller
GUI
Rule 5 — Không return None khi có thể raise Exception

Ví dụ

❌

return None

khi Google Maps lỗi.

Đúng:

raise TimeoutError(...)

Provider sẽ quyết định retry.

Rule 6 — Engine không log

Không

logger.info(...)

Không

print(...)

Engine chỉ:

thao tác browser
raise exception

Logging thuộc Provider.

Rule 7 — Unit Test phải mock toàn bộ Playwright

Không mở Chrome.

Không internet.

Không Google Maps thật.

Mock:

Page

↓

Locator

↓

Parser

Test sẽ chạy trong vài trăm mili giây.

Rule 8 — Không over-engineering

Ví dụ tôi đã thay đổi quyết định:

Ban đầu:

BrowserManager

↓

Sau review:

Bỏ luôn.

Đó là quyết định đúng.

Nếu sau này có:

Selenium
Edge
Firefox
nhiều browser

thì mới tách.

Rule 9 — Freeze là bất biến

Sau khi Freeze:

Không refactor vì:

"đẹp hơn"

Chỉ sửa nếu:

bug
performance
security
architecture issue

Đây là kỷ luật rất quan trọng trong dự án dài hạn.

Rule 10 — Ưu tiên sự rõ ràng hơn sự thông minh

Ví dụ:

Thay vì:

return GoogleMapsParser.parse(page)

viết một lambda phức tạp hoặc meta-programming.

Tôi luôn chọn code mà một lập trình viên mới có thể hiểu sau vài phút đọc.