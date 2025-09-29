# required libraries for selenium
from __future__ import annotations

import random
# program utilities
import sys
import time
from contextlib import contextmanager
# datetime for handling dates and times
from datetime import datetime, timezone
from typing import List

import pandas as pd
# beautifulsoup for parsing HTML
from bs4 import BeautifulSoup as bs
from selenium import webdriver
from selenium.common.exceptions import (NoSuchElementException,
                                        SessionNotCreatedException,
                                        TimeoutException, WebDriverException)
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
# from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
# from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# configs
from src.entity.config_entity import BotConfig
from src.exception.base import CustomException
from src.exception.selenium_exceptions import SeleniumException
from src.logger.logging_setup import get_logger
from src.utils import calculate_duration

service_name = "SeleniumBotService"

logging = get_logger(service_name)

class SeleniumBot:

    def __init__(self, selenium_config: BotConfig):
        self.config = selenium_config

    def _init_driver(self):
        start_time = time.perf_counter()
        options = webdriver.ChromeOptions()

        if self.config.HEADLESS:
            options.add_argument("--headless")

        options.add_argument("--disable-gpu")
        options.add_argument("--start-maximized")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        # --- Start of new retry logic ---
        if self.config.SELENIUM_REMOTE_URL:
            retries = self.config.RETRY_ATTEMPTS  # Number of retry attempts

            for attempt in range(retries):
                try:
                    logging.info(
                        f"Attempting to connect to remote driver (Attempt {attempt + 1}/{retries})...",
                        extra={
                            "service": service_name,
                            "host": self.config.SELENIUM_HOST,
                            "duration_ms": calculate_duration(start_time),
                        }
                    )

                    driver = webdriver.Remote(
                    command_executor=self.config.SELENIUM_REMOTE_URL,
                    options=options
                    )

                    logging.info("Successfully connected to remote driver.")
                    return driver
                except SessionNotCreatedException as e:
                    if attempt < retries - 1:
                        logging.warning(
                            f"Session not created: {e}. Retrying in 5 seconds...",
                            extra={
                                "service": service_name,
                                "host": self.config.SELENIUM_HOST,
                                "stack_trace": str(e),
                                "duration_ms": calculate_duration(start_time),
                            }
                        )
                        time.sleep(5)
                    else:
                        logging.error(
                            f"Failed to start a new session after {retries} attempts.",
                            extra={
                                "service": service_name,
                                "host": self.config.SELENIUM_HOST,
                                "stack_trace": str(e),
                                "duration_ms": calculate_duration(start_time),
                            }
                        )
                        raise CustomException(e, sys)

            # This part is technically unreachable due to the 'raise e' above, but good practice
            raise CustomException("Failed to initialize remote driver after multiple retries.", sys)
        # --- End of new retry logic ---
        else:
            return webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )

    @contextmanager
    def selenium_session(self):
        """
        Context manager to use a short-lived WebDriver session.
        """
        start_time = time.perf_counter()
        driver = None
        try:
            driver = self._init_driver()
            yield driver  # return driver to context
        except Exception as e:
            logging.error(
                f"Driver error: {e}",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise
        finally:
            if driver:
                driver.quit()
                logging.info(
                    "WebDriver session closed.",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )


    def open_site(self, driver: webdriver, target_url: str) -> webdriver:
        """
        Open the target URL with retry if the session dies.
        Returns:
            webdriver: A (possibly new) driver instance
        """
        start_time = time.perf_counter()
        for attempt in range(self.config.RETRY_ATTEMPTS):
            try:
                driver.get(target_url)
                logging.info(
                    f"Navigated to {target_url}",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )
                return driver  # success
            except WebDriverException as e:
                logging.error(
                    f"[Attempt {attempt + 1}] Failed to open {target_url}: {e}",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "stack_trace": str(e),
                        "duration_ms": calculate_duration(start_time),
                    }
                )
                if attempt < self.config.RETRY_ATTEMPTS - 1:
                    logging.info(
                        "Retrying with a fresh WebDriver...",
                        extra={
                            "service": service_name,
                            "host": self.config.SELENIUM_HOST,
                            "duration_ms": calculate_duration(start_time),
                        }
                    )
                    try:
                        driver.quit()
                    except Exception as e:
                        logging.error(
                            "Error while quiting the driver session",
                            extra={
                                "service": service_name,
                                "host": self.config.SELENIUM_HOST,
                                "stack_trace": str(e),
                                "duration_ms": calculate_duration(start_time),
                            }
                        )

                    driver = self._init_driver()
                    time.sleep(3)  # optional backoff
                else:
                    logging.critical(
                        "Some error occured in selenium while interacting with layout, please check image logs",
                        extra={
                            "service": service_name,
                            "host": self.config.SELENIUM_HOST,
                            # "stack_trace": str(e),
                            "duration_ms": calculate_duration(start_time),
                        }
                    )
                    # raise SeleniumException(e, sys, driver, "open_site")
                    # raise CustomException(e, sys)


    def close_login_popup_if_present(self, driver: webdriver) -> None:
        start_time = time.perf_counter()
        try:
            driver.switch_to.default_content()
            WebDriverWait(driver, self.config.POPUP_TIMEOUT).until(
                EC.presence_of_element_located((By.NAME, self.config.IFRAME_LOGIN_PAGE_SELECTOR))
            )

            iframe = driver.find_element(By.NAME, self.config.IFRAME_LOGIN_PAGE_SELECTOR)
            driver.switch_to.frame(iframe)

            continue_btn = WebDriverWait(driver, self.config.POPUP_TIMEOUT).until(
                EC.element_to_be_clickable((By.CLASS_NAME, self.config.CONTINUE_BUTTON_CLASS_SELECTOR))
            )

            driver.execute_script("arguments[0].click();", continue_btn)
            logging.debug(
                "Clicked 'Continue' button and closed popup.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "duration_ms": calculate_duration(start_time),
                }
            )
            driver.switch_to.default_content()

        except (TimeoutException, NoSuchElementException):
            logging.error(
                "Login popup not found or already closed.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "duration_ms": calculate_duration(start_time),
                }
            )
            driver.switch_to.default_content()

        except Exception as e:
            logging.error(
                "Error during login popup handling, for more please check image logs.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            driver.switch_to.default_content()
            raise SeleniumException(e, sys, driver, "close_login_popup_if_present")


    def is_login_popup_closed(self, driver: webdriver) -> bool:
        driver.switch_to.default_content()
        try:
            driver.find_element(By.NAME, self.config.IFRAME_LOGIN_PAGE_SELECTOR)
            return False
        except NoSuchElementException:
            return True


    def close_registration_popup_if_present(self, driver: webdriver) -> None:
        start_time = time.perf_counter()
        try:
            driver.switch_to.default_content()

            WebDriverWait(driver, self.config.POPUP_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config.IFRAME_REGISTRATION_PAGE_SELECTOR))
            )

            iframe = driver.find_element(By.CSS_SELECTOR, self.config.IFRAME_REGISTRATION_PAGE_SELECTOR)
            driver.switch_to.frame(iframe)

            close_btn = WebDriverWait(driver, self.config.POPUP_TIMEOUT).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, self.config.CLOSE_BUTTON_CLASS_SELECTOR))
            )

            driver.execute_script("arguments[0].click();", close_btn)
            logging.debug(
                "Clicked 'Close' button and closed popup.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "duration_ms": calculate_duration(start_time),
                }
            )
            driver.switch_to.default_content()

        except (TimeoutException, NoSuchElementException):
            logging.error(
                "Registration popup not found or already closed.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "duration_ms": calculate_duration(start_time),
                }
            )
            driver.switch_to.default_content()
        except Exception as e:
            logging.error(
                "Error during registration popup handling, for more please check image logs.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            driver.switch_to.default_content()
            raise SeleniumException(e, sys, driver, "close_registration_popup_if_present")


    def is_registration_popup_closed(self, driver: webdriver) -> bool:
        driver.switch_to.default_content()
        try:
            driver.find_element(By.CSS_SELECTOR, self.config.IFRAME_REGISTRATION_PAGE_SELECTOR)
            return False
        except NoSuchElementException:
            return True

    def handle_popup(self, driver: webdriver) -> None:
        start_time = time.perf_counter()
        try:
            # self.close_login_popup_if_present(driver)
            # time.sleep(1)
            if not self.is_login_popup_closed(driver):
                # logging.warning("Login popup is still open, attempting to close again.")
                logging.warning(
                    "Login popup is open, attempting to close.",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )
                self.close_login_popup_if_present(driver)
                time.sleep(1)

            # self.close_registration_popup_if_present(driver)
            # time.sleep(1)
            if not self.is_registration_popup_closed(driver):
                # logging.warning("Registration popup is still open, attempting to close again.")
                logging.warning(
                    "Registration popup is open, attempting to close.",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )
                self.close_registration_popup_if_present(driver)
                time.sleep(1)

        except Exception as e:
            logging.error(
                "Error handling popups, For more please check image logs",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise SeleniumException(e, sys, driver, "handle_popup")


    def get_pagination_number_of_pages(self, driver: webdriver) -> int:

        start_time = time.perf_counter()

        text = "" # Defined in outer scope to prevent 'undefined variable' issue

        try:
            pagination_element = WebDriverWait(driver, self.config.POPUP_TIMEOUT).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, self.config.PAGINATION_SELECTOR))
            )
            text = pagination_element.text # Extracted text safely
            total_pages = int(text.split()[-1]) # Basic parsing, may assume "1... X" format
            logging.debug(
                f"Total pages found: {total_pages}",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "duration_ms": calculate_duration(start_time),
                }
            )
            return total_pages

        except ValueError as e:
            logging.warning(
                f"Unexpected pagination format: '{text}'. Defaulting to 1 page.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            return 1 # Safe fallback

        except (TimeoutException, NoSuchElementException) as e:
            logging.warning(
                "Pagination element not found. Assuming there is only one page.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            return 1 # Safe fallback when pagination not rendered

        except Exception as e:
            # Catch any other unexpected exceptions
            logging.error(
                "An unexpected error occurred while finding pagination, For more please check image logs.",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise SeleniumException(e, sys, driver, "get_pagination_number_of_pages")


    def convert_to_datetime(self, text: str)-> datetime:
        """
        Convert a string representation of time into a datetime object.
        Args:
            text (str): A string representing time, either in the format "X days ago", "X hrs ago", etc., or a date string like "01 Jan 2023".
        Returns:
            datetime: A datetime object representing the time.
        """
        start_time = time.perf_counter()
        try:
            # current time
            now = datetime.now(timezone.utc)
            # removing inconsistancies
            time_diff, time_type, time_long = "", "", ""
            time_diff, time_type, time_long = text.lower().split()

            if time_long == "ago":
                if time_type == "day" or time_type == "days":
                    return now - pd.Timedelta(days=int(time_diff))
                elif time_type == "hrs" or time_type == "hour" or time_type == "hours":
                    return now - pd.Timedelta(hours=int(time_diff))
                elif time_type == "mins" or time_type == "minute" or time_type == "minutes":
                    return now - pd.Timedelta(minutes=int(time_diff))
                elif time_type == "secs" or time_type == "second" or time_type == "seconds":
                    return now - pd.Timedelta(seconds=int(time_diff))
                else:
                    return now
            else:
                dt = datetime.strptime(text, "%d %b %Y")
                return dt.replace(tzinfo=timezone.utc)

        except Exception as e:
            logging.error(
                "Error while convert_to_datetime",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise CustomException(e, sys)

    def random_delay(self, min_seconds: int=1, max_seconds: int=5):
        start_time = time.perf_counter()
        delay = random.uniform(min_seconds, max_seconds) # nosec
        logging.debug(
            f"Sleeping for {delay:.2f} seconds to mimic human behavior.",
            extra={
                "service": service_name,
                "host": self.config.SELENIUM_HOST,
                "duration_ms": calculate_duration(start_time),
            }
        )
        time.sleep(delay)


    def get_article_links(self, total_pagination_pages: int, str_date: str, date_format="%Y-%m-%d" ):
        start_time = time.perf_counter()
        try:
            links_list = []

            for page in range(1, total_pagination_pages + 1):

                with self.selenium_session() as driver:

                    # assign driver to instance variable for use in other methods
                    date = datetime.strptime(str_date, date_format)

                    # convert date string to datetime object
                    target_url = self.config.BASE_URL.format(year=date.year, month=date.month, day=date.day, page_no=page)

                    # random delays within a range to mimic human behavior better
                    self.random_delay(self.config.MIN_HUMAN_DELAY, self.config.MAX_HUMAN_DELAY)

                    # open site
                    driver = self.open_site(driver, target_url)

                    # close popups if present
                    self.handle_popup(driver)

                    # extract article links_list
                    soup = bs(driver.page_source, "html.parser")

                    link_segments = soup.find("div", attrs={"class": "sc-5a5e8d88-1 gxBCkm"})\
                                        .find_all("div", attrs={"data-testid": "liverpool-card"})

                    # iterate through each article and extract the link
                    for card in link_segments:
                        # check if article has the link attribute
                        link = card.find("a").get("href")
                        logging.debug(
                            f"Extracted link: https://www.bbc.com{link}",
                            extra={
                                "service": service_name,
                                "host": self.config.SELENIUM_HOST,
                                "duration_ms": calculate_duration(start_time),
                            }
                        )
                        links_list.append('https://www.bbc.com'+link)

            return links_list

        except Exception as e:
            logging.error(
                f"Error in get_article_links: {e}",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise CustomException(e, sys)


    def run_archive_scraper_selenium_bot(self, str_date: str, date_format="%Y-%m-%d") -> List[str]:
        start_time = time.perf_counter()
        try:
            # starting a fresh selenium session
            with self.selenium_session() as driver:

                total_pages = 0

                # assign driver to instance variable for use in other methods
                date = datetime.strptime(str_date, date_format)

                # convert date string to datetime object
                target_url = self.config.BASE_URL.format(year=date.year, month=date.month, day=date.day, page_no=1)

                # open site
                driver = self.open_site(driver, target_url)

                # close popups if present
                self.handle_popup(driver)

                # get total pages
                total_pages = self.get_pagination_number_of_pages(driver)
                logging.info(
                    f"Total pages found: {total_pages}",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )

            # get all article links from all pages
            if total_pages > 1:
                links_list = self.get_article_links(total_pagination_pages=total_pages, str_date=str_date, date_format=date_format)
                logging.info(
                    f"Total article links found: {len(links_list)}",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )
            else:
                logging.info(
                    "Only one page found, extracting links from the single page.",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )
                links_list = self.get_article_links(total_pagination_pages=1, str_date=str_date, date_format=date_format)
                logging.info(
                    f"Total article links found: {len(links_list)}",
                    extra={
                        "service": service_name,
                        "host": self.config.SELENIUM_HOST,
                        "duration_ms": calculate_duration(start_time),
                    }
                )

            return links_list

        except Exception as e:
            logging.error(
                f"An error occurred in [run_archive_scrapper_selenium_bot]: {e}",
                extra={
                    "service": service_name,
                    "host": self.config.SELENIUM_HOST,
                    "stack_trace": str(e),
                    "duration_ms": calculate_duration(start_time),
                }
            )
            raise CustomException(e, sys)

    def quit(self, driver: webdriver = None) -> None:
        start_time = time.perf_counter()
        driver.quit()
        logging.debug(
            "Driver closed.",
            extra={
                "service": service_name,
                "host": self.config.SELENIUM_HOST,
                "duration_ms": calculate_duration(start_time),
            }
        )
