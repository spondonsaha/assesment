"""SauceDemo inventory page (product list + hamburger menu + cart badge)."""

from __future__ import annotations

import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from ui.pages.base_page import BasePage


class InventoryPage(BasePage):
    INVENTORY_LIST = (By.CLASS_NAME, "inventory_list")
    INVENTORY_ITEMS = (By.CLASS_NAME, "inventory_item")
    ITEM_NAMES = (By.CLASS_NAME, "inventory_item_name")

    SORT_SELECT = (By.CLASS_NAME, "product_sort_container")

    CART_LINK = (By.CLASS_NAME, "shopping_cart_link")
    CART_BADGE = (By.CLASS_NAME, "shopping_cart_badge")

    # Hamburger menu
    MENU_BUTTON = (By.ID, "react-burger-menu-btn")
    MENU_WRAP = (By.CLASS_NAME, "bm-menu-wrap")
    CLOSE_BUTTON = (By.CLASS_NAME, "bm-cross-button")
    RESET_LINK = (By.ID, "reset_sidebar_link")
    LOGOUT_LINK = (By.ID, "logout_sidebar_link")

    LOGIN_BUTTON = (By.ID, "login-button")

    def is_loaded(self) -> bool:
        return self.is_displayed(self.INVENTORY_LIST)

    @allure.step("Wait for the inventory page to load")
    def wait_loaded(self):
        self.wait_visible(self.INVENTORY_LIST)
        return self

    # -- sorting -------------------------------------------------------------
    @allure.step("Sort products by '{value}'")
    def sort_by(self, value: str):
        """value: 'az' | 'za' | 'lohi' | 'hilo'."""
        select = Select(self.wait_visible(self.SORT_SELECT))
        select.select_by_value(value)
        return self

    # -- products ------------------------------------------------------------
    def product_names(self) -> list[str]:
        return self.texts_of(self.ITEM_NAMES)

    def first_product_name(self) -> str:
        return self.texts_of(self.ITEM_NAMES)[0]

    def _item_card(self, product_name: str):
        def find():
            for item in self.driver.find_elements(*self.INVENTORY_ITEMS):
                name_el = item.find_elements(By.CLASS_NAME, "inventory_item_name")
                if name_el and name_el[0].text == product_name:
                    return item
            raise AssertionError(f"Product not found on inventory page: {product_name!r}")

        return self._retry_on_stale(find)

    @allure.step("Add product to cart: '{product_name}'")
    def add_to_cart(self, product_name: str):
        before = self.cart_count()

        def _click():
            item = self._item_card(product_name)
            button = item.find_element(By.TAG_NAME, "button")
            self.driver.execute_script("arguments[0].click();", button)

        # React re-renders the card on click, so retry stale references and
        # wait on the badge count rather than holding the button element.
        self._retry_on_stale(_click)
        self.wait.until(lambda d: self.cart_count() == before + 1)
        return self

    @allure.step("Add the first product on the page to the cart")
    def add_first_to_cart(self):
        return self.add_to_cart(self.first_product_name())

    # -- cart ----------------------------------------------------------------
    def cart_count(self) -> int:
        if not self.is_displayed(self.CART_BADGE):
            return 0
        return int(self.text_of(self.CART_BADGE))

    @allure.step("Go to the cart")
    def go_to_cart(self):
        self.click(self.CART_LINK)
        self.wait_url_contains("cart.html")
        return self

    # -- menu ----------------------------------------------------------------
    def menu_is_open(self) -> bool:
        def _check():
            wrap = self.driver.find_element(*self.MENU_WRAP)
            return wrap.get_attribute("aria-hidden") == "false"

        return self._retry_on_stale(_check)

    @allure.step("Open the hamburger menu")
    def open_menu(self):
        if not self.menu_is_open():
            self.click(self.MENU_BUTTON)
        self.wait_clickable(self.RESET_LINK)
        return self

    @allure.step("Close the hamburger menu")
    def close_menu(self):
        if self.menu_is_open():
            self.click(self.CLOSE_BUTTON)
            self.wait_invisible(self.RESET_LINK)
        return self

    @allure.step("Reset App State from the hamburger menu")
    def reset_app_state(self):
        self.open_menu()
        self.click(self.RESET_LINK)
        # A successful reset clears the cart badge.
        self.wait_invisible(self.CART_BADGE, timeout=self.timeout)
        self.close_menu()
        return self

    @allure.step("Log out from the hamburger menu")
    def logout(self):
        self.open_menu()
        self.click(self.LOGOUT_LINK)
        self.wait_url_contains("saucedemo.com")
        self.wait_visible(self.LOGIN_BUTTON)
        return self
