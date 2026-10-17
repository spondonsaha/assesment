"""SauceDemo checkout pages: information, overview and complete."""

from __future__ import annotations

import re

import allure
from selenium.webdriver.common.by import By

from ui.pages.base_page import BasePage

_MONEY = re.compile(r"[\d.]+")


def _to_float(text: str) -> float:
    match = _MONEY.search(text or "")
    if not match:
        raise AssertionError(f"Cannot parse a price from: {text!r}")
    return float(match.group())


class CheckoutPage(BasePage):
    # Step one - customer information
    FIRST_NAME = (By.ID, "first-name")
    LAST_NAME = (By.ID, "last-name")
    POSTAL_CODE = (By.ID, "postal-code")
    CONTINUE = (By.ID, "continue")

    # Step two - overview
    ITEM_NAMES = (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
    ITEM_PRICES = (By.CSS_SELECTOR, ".cart_item .inventory_item_price")
    SUBTOTAL = (By.CLASS_NAME, "summary_subtotal_label")
    TAX = (By.CLASS_NAME, "summary_tax_label")
    TOTAL = (By.CLASS_NAME, "summary_total_label")
    FINISH = (By.ID, "finish")

    # Step three - complete
    COMPLETE_HEADER = (By.CLASS_NAME, "complete-header")
    COMPLETE_TEXT = (By.CLASS_NAME, "complete-text")
    BACK_HOME = (By.ID, "back-to-products")

    # -- step one ------------------------------------------------------------
    @allure.step("Fill checkout information (first/last/zip)")
    def fill_information(self, first: str = "John", last: str = "Doe", zip_code: str = "12345"):
        self.type(self.FIRST_NAME, first)
        self.type(self.LAST_NAME, last)
        self.type(self.POSTAL_CODE, zip_code)
        return self

    @allure.step("Continue to the checkout overview")
    def continue_to_overview(self):
        self.click(self.CONTINUE)
        self.wait_url_contains("checkout-step-two.html")
        return self

    # -- step two ------------------------------------------------------------
    def product_names(self) -> list[str]:
        return self.texts_of(self.ITEM_NAMES)

    def item_prices(self) -> list[float]:
        return [_to_float(t) for t in self.texts_of(self.ITEM_PRICES)]

    def subtotal(self) -> float:
        return _to_float(self.text_of(self.SUBTOTAL))

    def tax(self) -> float:
        return _to_float(self.text_of(self.TAX))

    def total(self) -> float:
        return _to_float(self.text_of(self.TOTAL))

    @allure.step("Finish the purchase")
    def finish(self):
        self.click(self.FINISH)
        self.wait_url_contains("checkout-complete.html")
        return self

    # -- step three ----------------------------------------------------------
    @allure.step("Read order confirmation header")
    def complete_header(self) -> str:
        return self.text_of(self.COMPLETE_HEADER)

    @allure.step("Return to the products page")
    def back_home(self):
        self.click(self.BACK_HOME)
        self.wait_url_contains("inventory.html")
        return self
