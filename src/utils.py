import json
import os
import random
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from typing import Any


def path(path_in_project: str) -> str:
    return os.path.abspath(__file__).replace(
        os.path.normpath("src/utils.py"), ""
    ) + os.path.normpath(path_in_project)


def load_config() -> dict:
    default_config = {
        "webdriver": "firefox",
        "verify_email_address": True,
        "authentic_input": True,
        "create_authentic_account": True,
        "audio_language": "en",
    }

    if not os.path.exists(path("config.json")):
        with open(path("config.json"), "x") as config_file:
            json.dump(default_config, config_file, indent=4)
            config_data = default_config.copy()

    else:
        with open(path("config.json"), "r") as config_file:
            config_data = json.load(config_file)

    return config_data


def send_input(webelement: WebElement, string: str, authentic: bool = True) -> None:
    if authentic:
        for char in string:
            webelement.send_keys(char)
            time.sleep(random.uniform(0.05, 0.1))

    else:
        webelement.send_keys(string)


def wait_for_element(
    webdriver: WebDriver, by: str, locator: str, custom_timeout: int = 10
) -> WebElement:
    return WebDriverWait(webdriver, custom_timeout).until(
        expected_conditions.visibility_of_element_located((by, locator))
    )
