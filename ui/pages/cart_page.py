"""SauceDemo cart page."""

from __future__ import annotations

import allure
from selenium.webdriver.common.by import By

from ui.pages.base_page import BasePage


class CartPage(BasePage):
    CART_ITEMS = (By.CLASS_NAME, "cart_item")
    ITEM_NAMES = (By.CSS_SELECTOR, ".cart_item .inventory_item_name")
    ITEM_PRICES = (By.CSS_SELECTOR, ".cart_item .inventory_item_price")

    CHECKOUT_BUTTON = (By.ID, "checkout")
    CONTINUE_SHOPPING = (By.ID, "continue-shopping")

    def is_loaded(self) -> bool:
        return self.is_displayed(self.CHECKOUT_BUTTON)

    @allure.step("Wait for the cart page to load")
    def wait_loaded(self):
        self.wait_visible(self.CHECKOUT_BUTTON)
        return self

    def product_names(self) -> list[str]:
        return self.texts_of(self.ITEM_NAMES)

    @allure.step("Proceed to checkout")
    def checkout(self):
        self.click(self.CHECKOUT_BUTTON)
        self.wait_url_contains("checkout-step-one.html")
        return self
