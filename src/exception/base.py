import os
import sys


def error_message_detail(error, error_detail):
    # tb = error_detail.exc_info()[2]
    _, _, tb = sys.exc_info()
    if tb is None:
        file_name = "Unknown"
        line_number = "Unknown"
    else:
        file_name = os.path.split(tb.tb_frame.f_code.co_filename)[1]
        line_number = tb.tb_lineno

    error_message = (
        "Error occurred python script name [{0}] line number [{1}] error message [{2}]"
    ).format(file_name, line_number, str(error))

    return error_message

class CustomException(Exception):
    def __init__(self, error_message, error_detail):
        """Raise exception in string format"""
        super().__init__(str(error_message))
        self.error_message = error_message_detail(
            error_message, error_detail=error_detail
        )

    def __str__(self):
        return self.error_message
