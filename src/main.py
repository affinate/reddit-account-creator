import os
import random
import re
import time

from customization import generate_account_username, generate_account_password
from selenium import webdriver
from selenium.webdriver.common.by import By
from solver import RecaptchaSolver
from utils import load_config, send_input, wait_for_element, path


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.84 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/100.0.1185.29",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12.3; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.141 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36 Edg/99.0.1150.36",
]


EMAIL_REGEX = re.compile(r".*@[a-zA-Z0-9\-]*\.[a-zA-Z0-9]{1,10}")
VERIFICATION_URL_REGEX = re.compile(
    r"https://www\.reddit\.com/verification/[a-zA-Z0-9\?_=\-&]+"
)


config = load_config()

config_webdriver = config.get("webdriver").lower()
config_vea = config.get("verify_email_address")
config_authentic_input = config.get("authentic_input")
config_caa = config.get("create_authentic_account")
config_audio_language = config.get("audio_language").lower()


assert config_webdriver in ("firefox", "chrome"), "Unkown webdriver name in config file"

if config_webdriver == "firefox":
    WebDriver = webdriver.Firefox

    options = webdriver.FirefoxOptions()
    options.set_preference("general.useragent.override", random.choice(USER_AGENTS))

elif config_webdriver == "chrome":
    WebDriver = webdriver.Chrome

    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={random.choice(USER_AGENTS)}")


account_email_address = "email@email.com"

if config_vea:
    mail_driver = WebDriver(options=options)
    mail_driver.get("https://internxt.com/temporary-email")

    time.sleep(2)

    for p_tag_element in mail_driver.find_elements(By.TAG_NAME, "p"):
        if re_match := EMAIL_REGEX.match(p_tag_element.text):
            account_email_address = re_match.string
            break

    else:
        raise Exception(
            "Unable to get email address, therefore unable to verify account"
        )


reddit_driver = WebDriver(options=options)
reddit_driver.get("https://reddit.com/register")

reddit_email_input = wait_for_element(reddit_driver, By.ID, "regEmail")
send_input(reddit_email_input, account_email_address, config_authentic_input)

wait_for_element(reddit_driver, By.CLASS_NAME, "AnimatedForm__submitButton").click()

time.sleep(2)

account_username = generate_account_username(reddit_driver)
account_password = generate_account_password()

reddit_username_input = wait_for_element(reddit_driver, By.ID, "regUsername")
send_input(reddit_username_input, account_username, config_authentic_input)

time.sleep(0.5)

reddit_password_input = wait_for_element(reddit_driver, By.ID, "regPassword")
send_input(reddit_password_input, account_password, config_authentic_input)

time.sleep(1)

captcha_solver = RecaptchaSolver(
    webdriver=reddit_driver, language=config_audio_language
)

try:
    captcha_solver.solve()

except Exception as exception:
    reddit_driver.close()

    if config_vea:
        mail_driver.close()

wait_for_element(reddit_driver, By.CLASS_NAME, "SignupButton").click()

try:
    wait_for_element(
        reddit_driver,
        By.XPATH,
        '//span[@class="AnimatedForm__submitStatus m-error"]',
        5,
    )

    print("IP got ratelimited, closing program")

    reddit_driver.close()

    if config_vea:
        mail_driver.close()

    exit()

except Exception:
    pass

print("Account created!")

authentic = False

if config_caa:
    time.sleep(2)

    # Reject cookies button
    wait_for_element(
        reddit_driver,
        By.XPATH,
        '//button[@class="_1tI68pPnLBjR1iHcL7vsee _2iuoyPiKHN3kfOoeIQalDT _10BQ7pjWbeYP63SAPNS8Ts HNozj_dKjQZ59ZsfEegz8 "]',
    ).click()

    time.sleep(1)

    # Selects a random gender option
    gender_elements = reddit_driver.find_elements(
        By.XPATH, '//input[@name="genderCollection"]'
    )

    random.choice(gender_elements).click()

    time.sleep(2)

    # Selects 3 random topics
    interesting_topics = reddit_driver.find_elements(
        By.XPATH,
        '//button[@class="_3oCL2oMbe3H81mue3bR1CQ  _2iuoyPiKHN3kfOoeIQalDT _10BQ7pjWbeYP63SAPNS8Ts HNozj_dKjQZ59ZsfEegz8 "]',
    )[:14]

    random.shuffle(interesting_topics)

    for i in range(3):
        interesting_topics[i].click()

    reddit_driver.find_element(
        By.XPATH, '//button[@class="dK60vCQAai2JPR7mVZ4ir"]'
    ).click()

    time.sleep(2)

    # Select random subreddits
    reddit_driver.find_elements(By.XPATH, '//button[@class="_3CPhqReN6aQjDfxC-MaWG4"]')[
        0
    ].click()

    # Submit
    for _ in range(2):
        reddit_driver.find_element(
            By.XPATH, '//button[@class="dK60vCQAai2JPR7mVZ4ir"]'
        ).click()

        time.sleep(2)

    authentic = True


verfied_email = False

if config_vea:
    time.sleep(10)

    print("Verifying email...")

    wait_for_element(
        mail_driver,
        By.XPATH,
        '//p[@title="Verify your Reddit email address"]/ancestor::button[1]',
    ).click()

    for a_tag in mail_driver.find_elements(By.TAG_NAME, "a"):
        if a_tag is None:
            continue

        if a_tag.get_attribute("href") is None:
            continue

        l = VERIFICATION_URL_REGEX.findall(a_tag.get_attribute("href"))

        if len(l) > 0:
            mail_driver.get(l[0])
            print("Verified email.")
            break

    wait_for_element(mail_driver, By.CLASS_NAME, "verify-button").click()

    verfied_email = True

    mail_driver.close()

if not os.path.exists(path("accounts/")):
    os.mkdir(path("accounts/"))

with open(path(f"accounts/{account_username}.txt"), "x") as file:
    file.write(
        f"Username: {account_username}\n"
        f"Password: {account_password}\n"
        f"Email: {account_email_address}\n"
        f"Verified: {verfied_email}\n"
        f"Authentic: {authentic}"
    )

    print("Saved account to file")


reddit_driver.close()
