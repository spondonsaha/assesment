"""Base page object with explicit-wait helpers shared by all pages."""

from __future__ import annotations

import allure
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from config import settings


class BasePage:
    def __init__(self, driver, timeout: int | None = None):
        self.driver = driver
        self.timeout = timeout or settings.UI_TIMEOUT
        self.wait = WebDriverWait(driver, self.timeout)

    # -- internal helpers ----------------------------------------------------
    def _retry_on_stale(self, func, retries: int = 4):
        """Run ``func`` retrying when React re-renders invalidate elements."""
        last_exc = None
        for _ in range(retries):
            try:
                return func()
            except StaleElementReferenceException as exc:
                last_exc = exc
        raise last_exc

    # -- waits ---------------------------------------------------------------
    def wait_visible(self, locator):
        try:
            return self.wait.until(EC.visibility_of_element_located(locator))
        except TimeoutException:
            self._dump(locator)
            raise

    def wait_clickable(self, locator):
        try:
            return self.wait.until(EC.element_to_be_clickable(locator))
        except TimeoutException:
            self._dump(locator)
            raise

    def wait_all_visible(self, locator):
        try:
            return self.wait.until(EC.visibility_of_all_elements_located(locator))
        except TimeoutException:
            self._dump(locator)
            raise

    def wait_present(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def wait_invisible(self, locator, timeout: int | None = None):
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.invisibility_of_element_located(locator))

    def wait_url_contains(self, fragment: str, timeout: int | None = None):
        wait = WebDriverWait(self.driver, timeout or self.timeout)
        return wait.until(EC.url_contains(fragment))

    # -- actions -------------------------------------------------------------
    def click(self, locator):
        self._retry_on_stale(lambda: self.wait_clickable(locator).click())

    def type(self, locator, text: str):
        def _type():
            el = self.wait_visible(locator)
            el.clear()
            el.send_keys(text)

        self._retry_on_stale(_type)

    def text_of(self, locator) -> str:
        return self._retry_on_stale(lambda: self.wait_visible(locator).text)

    def texts_of(self, locator) -> list[str]:
        return self._retry_on_stale(
            lambda: [el.text for el in self.wait_all_visible(locator)]
        )

    def is_displayed(self, locator) -> bool:
        els = self.driver.find_elements(*locator)
        return bool(els) and els[0].is_displayed()

    def execute_click(self, locator):
        """Native JS click used where normal clicks are flaky on SauceDemo."""
        def _js_click():
            el = self.wait_present(locator)
            self.driver.execute_script("arguments[0].click();", el)

        self._retry_on_stale(_js_click)

    # -- diagnostics ---------------------------------------------------------
    def _dump(self, locator):
        try:
            allure.attach(
                self.driver.get_screenshot_as_png(),
                name="timeout-screenshot",
                attachment_type=allure.attachment_type.PNG,
            )
        except Exception:
            pass
