from app.providers.google_web_provider import GoogleWebProvider
from app.providers.vietbando_web_provider import VietBanDoWebProvider


def test_vietbando_provider_uses_shared_web_provider_behavior() -> None:
    assert issubclass(VietBanDoWebProvider, GoogleWebProvider)
    assert VietBanDoWebProvider.PROVIDER_NAME == "vietbando_web"
