import os
import random
import requests
import time
import whisper

from utils import send_input, wait_for_element, path
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


class RecaptchaSolver:
    def __init__(
        self, webdriver: WebDriver, language: str = "en", model: str = "base"
    ) -> None:
        self._webdriver = webdriver
        self._language = language
        self._model = model

        self._whisper_model = whisper.load_model(self._model)

    def solve(self) -> None:
        recaptcha_iframe = wait_for_element(
            self._webdriver, By.XPATH, '//iframe[@title="reCAPTCHA"]'
        )

        self._webdriver.switch_to.frame(recaptcha_iframe)

        self._wait()

        captcha_checkbox = wait_for_element(self._webdriver, By.ID, "recaptcha-anchor")

        self._js_click(captcha_checkbox)

        if captcha_checkbox.get_attribute("aria-checked") == "true":
            return

        self._webdriver.switch_to.parent_frame()

        captcha_challenge = wait_for_element(
            self._webdriver,
            By.XPATH,
            '//iframe[contains(@src, "recaptcha") and contains(@src, "bframe")]',
        )

        self._webdriver.switch_to.frame(captcha_challenge)

        self._wait()

        wait_for_element(self._webdriver, By.ID, "recaptcha-audio-button").click()

        self._solve_audio_challenge()

        self._wait()

        verify_button = wait_for_element(
            self._webdriver, By.ID, "recaptcha-verify-button"
        )

        self._js_click(verify_button)

        self._wait()

        while True:
            try:
                wait_for_element(self._webdriver, By.XPATH, '//div[@style=""]', 5)

                self._solve_audio_challenge()

                verify_button = wait_for_element(
                    self._webdriver, By.ID, "recaptcha-verify-button"
                )

                self._wait()

                self._js_click(verify_button)

            except Exception:
                break

        self._webdriver.switch_to.parent_frame()

        print("Captcha solved")

    def _solve_audio_challenge(self) -> None:
        def get_download_link() -> WebElement:
            try:
                download_link: WebElement = wait_for_element(
                    self._webdriver, By.CLASS_NAME, "rc-audiochallenge-tdownload-link"
                )

            except Exception:
                raise Exception(
                    "Automated queries were detected. Change your ip address."
                )

            return download_link

        def get_reload_button() -> WebElement:
            try:
                download_link: WebElement = wait_for_element(
                    self._webdriver, By.ID, "recaptcha-reload-button"
                )

            except Exception:
                raise Exception("Unexpected error.")

            return download_link

        audio_challenge_file = path("google_audio_challenge.mp3")

        with open(audio_challenge_file, "wb") as file:
            audio_link = get_download_link().get_attribute("href")

            audio_download = requests.get(audio_link, allow_redirects=True)

            while audio_download.status_code == 404:
                self._wait()
                get_reload_button().click()
                audio_link = get_download_link().get_attribute("href")
                audio_download = requests.get(audio_link, allow_redirects=True)

            file.write(audio_download.content)

        audio = whisper.load_audio(audio_challenge_file)
        audio = whisper.pad_or_trim(audio)

        mel = whisper.log_mel_spectrogram(audio).to(self._whisper_model.device)

        result = whisper.decode(
            model=self._whisper_model,
            mel=mel,
            options=whisper.DecodingOptions(language=self._language, fp16=False),
        )

        challenge_text = result.text

        if os.path.exists(audio_challenge_file):
            os.remove(audio_challenge_file)

        challenge_text_field = self._webdriver.find_element(By.ID, "audio-response")

        self._wait()
        self._wait()

        send_input(challenge_text_field, challenge_text.lower().strip(".?!,\"'"))

    def _js_click(self, element: WebElement) -> None:
        self._webdriver.execute_script("arguments[0].click()", element)

    def _wait(self) -> None:
        time.sleep(random.uniform(1, 2))
