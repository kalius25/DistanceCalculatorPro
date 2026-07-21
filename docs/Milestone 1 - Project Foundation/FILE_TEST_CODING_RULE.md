Tôi đề nghị thống nhất 5 quy tắc
1. Dùng Builder Functions

Như chúng ta đã làm:

make_request()
make_route()
make_result()
make_provider()

Engine cũng nên như vậy:

def make_page():
    return MagicMock()


def make_locator():
    return MagicMock()


def make_request():
    return RouteRequest(
        origin="Can Tho",
        destination="Ho Chi Minh",
        travel_mode=TravelMode.DRIVING,
        timeout=30,
    )


def make_route():
    return RouteOption(
        summary="Fastest",
        distance_text="10 km",
        duration_text="15 phút",
        distance_km=10,
        duration_minutes=15,
    )

Builder giúp toàn bộ test thống nhất và giảm rất nhiều code lặp.

2. Dùng pytest.mark.parametrize khi có nhiều trường hợp

Ví dụ Travel Mode.

Hiện nay chỉ có:

TravelMode.DRIVING

Nhưng tôi sẽ viết test như sau ngay từ đầu:

@pytest.mark.parametrize(
    "mode",
    [
        TravelMode.DRIVING,
    ],
)
def test_select_travel_mode(mode):
    engine = GoogleMapsEngine()

    page = make_page()
    locator = make_locator()

    engine._TRAVEL_MODE_LOCATORS = {
        mode: lambda _: locator,
    }

    request = make_request()
    request.travel_mode = mode

    engine._select_travel_mode(
        page,
        request,
    )

    locator.click.assert_called_once()

Sau này thêm:

TravelMode.WALKING
TravelMode.BICYCLING
TravelMode.TRANSIT

chỉ cần sửa:

[
    TravelMode.DRIVING,
    TravelMode.WALKING,
    TravelMode.BICYCLING,
    TravelMode.TRANSIT,
]

Không phải viết thêm test.

3. Không patch Playwright

Chỉ mock đúng interface project.

Ví dụ:

Page

↓

Locator

↓

Parser

Không bao giờ mock Chromium.

Không bao giờ start browser.

4. Không test implementation

Ví dụ không nên test:

assert engine._TRAVEL_MODE_LOCATORS

mà test hành vi:

locator.click.assert_called_once()

Nếu sau này implementation đổi, test vẫn chạy.

5. Một test chỉ kiểm tra một hành vi

Ví dụ:

test_validate_timeout()

↓

chỉ test timeout

không test luôn origin.

Đây là nguyên tắc tôi thấy đang rất hiệu quả ở các module trước.