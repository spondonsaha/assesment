"""SauceDemo login page."""

from __future__ import annotations

import allure
from selenium.webdriver.common.by import By

from config import settings
from ui.pages.base_page import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "h3[data-test='error']")
    ERROR_BUTTON = (By.CSS_SELECTOR, "button[data-test='error-button']")

    def load(self):
        self.driver.get(settings.UI_BASE_URL)
        self.wait_visible(self.LOGIN_BUTTON)
        return self

    @allure.step("Login as '{username}'")
    def login(self, username: str, password: str = settings.SAUCEDEMO_PASSWORD):
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.LOGIN_BUTTON)
        return self

    @allure.step("Read login error message")
    def error_message(self) -> str:
        return self.text_of(self.ERROR)

    @allure.step("Wait for the login page to load")
    def wait_loaded(self):
        self.wait_visible(self.LOGIN_BUTTON)
        return self

    def is_loaded(self) -> bool:
        return self.is_displayed(self.LOGIN_BUTTON)
