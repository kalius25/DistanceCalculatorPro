from app.exceptions import EngineException, ErrorCode


def test_details_property():
    ex = EngineException(
        "Engine timeout",
        cause=TimeoutError("Navigation timeout"),
        context={
            "timeout": 30,
        },
    )

    assert ex.details == {
        "message": "Engine timeout",
        "error_code": ErrorCode.ENGINE_ERROR.value,
        "cause": "TimeoutError('Navigation timeout')",
        "context": {
            "timeout": 30,
        },
    }