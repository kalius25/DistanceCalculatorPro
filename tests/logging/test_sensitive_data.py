from __future__ import annotations

import pytest

from app.logging.sensitive_data import (
    SensitiveDataSanitizer,
)


def test_sensitive_key_is_redacted():
    result = SensitiveDataSanitizer.sanitize_mapping(
        {
            "username": "admin",
            "password": "123456",
            "api_key": "secret-key",
        },
    )

    assert result == {
        "username": "admin",
        "password": "[REDACTED]",
        "api_key": "[REDACTED]",
    }


def test_nested_sensitive_key_is_redacted():
    result = SensitiveDataSanitizer.sanitize_mapping(
        {
            "request": {
                "headers": {
                    "Authorization": ("Bearer secret-token"),
                },
            },
        },
    )

    assert result == {
        "request": {
            "headers": {
                "Authorization": "[REDACTED]",
            },
        },
    }


def test_email_is_masked():
    result = SensitiveDataSanitizer.sanitize(
        "Contact duy.nguyen@example.com",
    )

    assert result == ("Contact d***@example.com")


def test_single_character_email_is_masked():
    result = SensitiveDataSanitizer.sanitize(
        "a@example.com",
    )

    assert result == "*@example.com"


def test_phone_is_masked():
    result = SensitiveDataSanitizer.sanitize(
        "Phone: 0912 345 678",
    )

    assert result == "Phone: ***5678"


def test_coordinates_are_redacted():
    result = SensitiveDataSanitizer.sanitize(
        "10.337437629699707,105.46455383300781",
    )

    assert result == ("[COORDINATES_REDACTED]")


def test_bearer_token_is_redacted():
    result = SensitiveDataSanitizer.sanitize(
        "Authorization: Bearer abc.def.ghi",
    )

    assert result == ("Authorization: Bearer [REDACTED]")


def test_secret_assignment_is_redacted():
    result = SensitiveDataSanitizer.sanitize(
        "password=my-secret",
    )

    assert result == ("password=[REDACTED]")


def test_long_string_is_truncated():
    result = SensitiveDataSanitizer.sanitize(
        "A" * 300,
    )

    assert result == ("A" * 256 + "...[TRUNCATED]")


def test_binary_value_is_not_logged():
    result = SensitiveDataSanitizer.sanitize(
        b"secret binary",
    )

    assert result == "[BINARY:13]"


def test_sequence_is_sanitized():
    result = SensitiveDataSanitizer.sanitize(
        [
            "user@example.com",
            "0912345678",
        ],
    )

    assert result == [
        "u***@example.com",
        "***5678",
    ]


def test_unsupported_object_uses_safe_string():
    class CustomValue:
        def __str__(self) -> str:
            return "safe-value"

    result = SensitiveDataSanitizer.sanitize(
        CustomValue(),
    )

    assert result == "safe-value"


def test_fingerprint_is_stable():
    first = SensitiveDataSanitizer.fingerprint(
        "  Can Tho  ",
    )
    second = SensitiveDataSanitizer.fingerprint(
        "can tho",
    )

    assert first == second
    assert len(first) == 16


def test_collection_is_truncated():
    result = SensitiveDataSanitizer.sanitize(
        list(range(25)),
    )

    assert result[:20] == list(range(20))
    assert result[20] == "[TRUNCATED]"


def test_mapping_is_truncated():
    source = {f"field_{index}": index for index in range(25)}

    result = SensitiveDataSanitizer.sanitize_mapping(source)

    assert (
        len(
            [key for key in result if key != "_truncated"],
        )
        == 20
    )

    assert result["_truncated"] is True


def test_maximum_depth_is_limited():
    value = {
        "level_1": {
            "level_2": {
                "level_3": {
                    "level_4": {
                        "level_5": {
                            "level_6": "secret",
                        },
                    },
                },
            },
        },
    }

    result = SensitiveDataSanitizer.sanitize(
        value,
    )

    assert "MAX_DEPTH" in str(result)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (None, None),
        (True, True),
        (False, False),
        (0, 0),
        (123, 123),
        (3.14, 3.14),
    ],
)
def test_sanitize_preserves_primitive_values(
    value,
    expected,
):
    assert SensitiveDataSanitizer.sanitize(value) == expected


def test_none_key_is_not_sensitive():
    result = SensitiveDataSanitizer._is_sensitive_key(
        None,
    )

    assert result is False


@pytest.mark.parametrize(
    "key",
    [
        "password",
        "api_key",
        "Authorization",
        "client-secret",
        "session id",
    ],
)
def test_sensitive_key_variations_are_detected(
    key,
):
    assert SensitiveDataSanitizer._is_sensitive_key(key) is True


def test_nested_sensitive_field_name_is_detected():
    result = SensitiveDataSanitizer._is_sensitive_key(
        "user_password_hash",
    )

    assert result is True


def test_normal_key_is_not_sensitive():
    result = SensitiveDataSanitizer._is_sensitive_key(
        "route_count",
    )

    assert result is False


def test_bytearray_is_not_logged():
    value = bytearray(
        b"secret",
    )

    result = SensitiveDataSanitizer.sanitize(
        value,
    )

    assert result == "[BINARY:6]"
