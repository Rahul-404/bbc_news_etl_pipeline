import logging
import os
import time

from src.exception.base import error_message_detail


class SeleniumException(Exception):
    def __init__(self, error_message, error_detail, driver=None, context: str = "unknown"):
        """
        Selenium-specific exception with screenshot capability.

        Args:
            error_message: The error message.
            error_detail: Exception details from sys.
            driver: Selenium WebDriver instance (optional).
            context: Context string for screenshot naming.
        """
        self.error_message = error_message_detail(error_message, error_detail)
        self.driver = driver
        self.screenshot_dir = os.path.join("logs", "screenshots")

        # Take screenshot if driver provided
        os.makedirs(self.screenshot_dir, exist_ok=True)
        if self.driver:
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            screenshot_name = os.path.join(self.screenshot_dir, f"screenshot_{context}_{timestamp}.png")
            try:
                self.driver.save_screenshot(screenshot_name)
                logging.error(f"[{context}] Screenshot saved: {screenshot_name}")
            except Exception as screenshot_error:
                logging.warning(f"Could not save screenshot: {screenshot_error}")

        super().__init__(self.error_message)

    def __str__(self):
        return self.error_message
