API Contract (AC)

Ví dụ

AC-001

BaseEngine

find_routes()

Input

RouteRequest

Output

list<RouteOption>
AC-002

BaseProvider

calculate()

Input

RouteRequest

Output

RouteResult




API Contract v1.0

Chúng ta vẫn nên khóa giao diện công khai ngay từ bây giờ.

GoogleMapsParser
class GoogleMapsParser:

    @staticmethod
    def parse(page: Page) -> list[RouteOption]:
        ...
GoogleMapsEngine
class GoogleMapsEngine:

    def find_routes(
        self,
        request: RouteRequest,
    ) -> list[RouteOption]:
        ...
GoogleMapsProvider
class GoogleMapsProvider:

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:
        ...
RouteService
class RouteService:

    def calculate(
        self,
        request: RouteRequest,
    ) -> RouteResult:
        ...

Đây sẽ là API Contract v1.0 của dự án.