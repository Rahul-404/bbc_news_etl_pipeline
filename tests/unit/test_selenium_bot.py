from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

import pytest
from selenium.common.exceptions import (NoSuchElementException,
                                        SessionNotCreatedException)

from src.components.selenium_bot import SeleniumBot
from src.entity.config_entity import BotConfig
from src.exception.base import CustomException


@pytest.fixture
def mock_config():
    return BotConfig(
        HEADLESS=True,
        SELENIUM_REMOTE_URL=None,
        SELENIUM_HOST="localhost",
        RETRY_ATTEMPTS=2,
        POPUP_TIMEOUT=1,
        IFRAME_LOGIN_PAGE_SELECTOR="login_iframe",
        CONTINUE_BUTTON_CLASS_SELECTOR="continue-btn",
        IFRAME_REGISTRATION_PAGE_SELECTOR="reg_iframe",
        CLOSE_BUTTON_CLASS_SELECTOR="close-btn",
        PAGINATION_SELECTOR="pagination",
        BASE_URL="https://fakeurl.com/archive/{year}/{month}/{day}?page={page_no}",
        MIN_HUMAN_DELAY=0,
        MAX_HUMAN_DELAY=0,
    )


def test_convert_to_datetime_relative(mock_config):
    bot = SeleniumBot(mock_config)
    now = datetime.now(timezone.utc)
    result = bot.convert_to_datetime("2 days ago")
    assert isinstance(result, datetime)
    assert (now - result).days in (1, 2)  # allow for timing offset


def test_convert_to_datetime_absolute(mock_config):
    bot = SeleniumBot(mock_config)
    result = bot.convert_to_datetime("01 Jan 2023")
    assert result == datetime(2023, 1, 1, tzinfo=timezone.utc)


def test_convert_to_datetime_invalid(mock_config):
    bot = SeleniumBot(mock_config)
    with pytest.raises(CustomException):
        bot.convert_to_datetime("not a date")


@patch("src.components.selenium_bot.webdriver.Chrome")
def test_init_driver_local(mock_webdriver, mock_config):
    bot = SeleniumBot(mock_config)
    driver = bot._init_driver()
    assert driver == mock_webdriver.return_value
    mock_webdriver.assert_called_once()


@patch("src.components.selenium_bot.webdriver.Remote")
def test_init_driver_remote_success(mock_remote, mock_config):
    mock_config.SELENIUM_REMOTE_URL = "http://fake:4444/wd/hub"
    bot = SeleniumBot(mock_config)
    driver = bot._init_driver()
    assert driver == mock_remote.return_value


@patch("src.components.selenium_bot.webdriver.Remote", side_effect=SessionNotCreatedException("fail"))
def test_init_driver_remote_failure(mock_remote, mock_config):
    mock_config.SELENIUM_REMOTE_URL = "http://fake:4444/wd/hub"
    bot = SeleniumBot(mock_config)
    with pytest.raises(CustomException):
        bot._init_driver()


def test_is_login_popup_closed_true(mock_config):
    bot = SeleniumBot(mock_config)
    driver = MagicMock()
    driver.find_element.side_effect = NoSuchElementException("not found")
    assert bot.is_login_popup_closed(driver) is True


def test_is_login_popup_closed_false(mock_config):
    bot = SeleniumBot(mock_config)
    driver = MagicMock()
    driver.find_element.return_value = True
    assert bot.is_login_popup_closed(driver) is False


def test_is_registration_popup_closed_true(mock_config):
    bot = SeleniumBot(mock_config)
    driver = MagicMock()
    driver.find_element.side_effect = NoSuchElementException("not found")
    assert bot.is_registration_popup_closed(driver) is True


def test_is_registration_popup_closed_false(mock_config):
    bot = SeleniumBot(mock_config)
    driver = MagicMock()
    driver.find_element.return_value = True
    assert bot.is_registration_popup_closed(driver) is False


def test_random_delay(mock_config):
    bot = SeleniumBot(mock_config)
    with patch("time.sleep") as mock_sleep:
        bot.random_delay(0, 0)
        mock_sleep.assert_called_once()


@patch("src.components.selenium_bot.SeleniumBot.get_article_links", return_value=["https://test.com/a", "https://test.com/b"])
@patch("src.components.selenium_bot.SeleniumBot.get_pagination_number_of_pages", return_value=2)
@patch("src.components.selenium_bot.SeleniumBot.open_site")
@patch("src.components.selenium_bot.SeleniumBot.selenium_session")
def test_run_archive_scraper(mock_session, mock_open, mock_pages, mock_links, mock_config):
    driver_mock = MagicMock()
    mock_session.return_value.__enter__.return_value = driver_mock
    bot = SeleniumBot(mock_config)
    links = bot.run_archive_scraper_selenium_bot("2023-01-01")
    assert len(links) == 2
    mock_pages.assert_called_once()
    mock_links.assert_called_once()


def test_quit(mock_config):
    bot = SeleniumBot(mock_config)
    driver = MagicMock()
    bot.quit(driver)
    driver.quit.assert_called_once()
