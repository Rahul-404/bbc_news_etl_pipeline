import sys

from src.exception.base import CustomException, error_message_detail


def test_error_message_with_traceback():
    try:
        1 / 0
    except ZeroDivisionError as e:
        detail = sys
        message = error_message_detail(e, detail)
        assert "division by zero" in message # nosec B101
        assert "line number" in message # nosec B101
        assert "python script name" in message # nosec B101

def test_error_message_without_traceback():
    class FakeErrorDetail:
        def exc_info(self):
            return (None, None, None)

    error = ValueError("Something went wrong")
    detail = FakeErrorDetail()

    message = error_message_detail(error, detail)
    assert "Unknown" in message # nosec B101
    assert "Something went wrong" in message # nosec B101

def test_custom_exception_with_valid_traceback():
    try:
        int("not-a-number")
    except ValueError as e:
        exception = CustomException(e, sys)
        assert isinstance(exception, CustomException) # nosec B101
        assert "invalid literal for int()" in str(exception) # nosec B101
        assert "line number" in str(exception) # nosec B101

def test_custom_exception_without_traceback():
    class FakeErrorDetail:
        def exc_info(self):
            return (None, None, None)

    error = RuntimeError("Fake error")
    exception = CustomException(error, FakeErrorDetail())
    assert "Unknown" in str(exception) # nosec B101
    assert "Fake error" in str(exception) # nosec B101
