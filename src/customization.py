import secrets

from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver


def generate_account_username(webdriver: WebDriver) -> str:
    """Change this to however you want to generate a username, or leave it as is"""

    return webdriver.find_elements(By.CLASS_NAME, "Onboarding__usernameSuggestion")[
        0
    ].text


def generate_account_password() -> str:
    """Change this to however you want to generate a password, or leave it as is"""

    return secrets.token_urlsafe(16)
