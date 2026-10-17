"""UI suite fixtures: Selenium WebDriver lifecycle."""

from __future__ import annotations

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.edge.options import Options as EdgeOptions

from ui.pages.cart_page import CartPage
from ui.pages.checkout_page import CheckoutPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.login_page import LoginPage


def _chrome_options(headed: bool) -> ChromeOptions:
    opts = ChromeOptions()
    if not headed:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--incognito")
    return opts


def _edge_options(headed: bool) -> EdgeOptions:
    opts = EdgeOptions()
    if not headed:
        opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1440,900")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-notifications")
    opts.add_argument("--inprivate")
    return opts


@pytest.fixture()
def driver(headed: bool, browser_name: str):
    """Fresh Selenium driver per test (Selenium Manager provisions the driver)."""
    if browser_name == "edge":
        drv = webdriver.Edge(options=_edge_options(headed))
    else:
        drv = webdriver.Chrome(options=_chrome_options(headed))
    drv.implicitly_wait(0)
    try:
        yield drv
    finally:
        drv.quit()


@pytest.fixture()
def login_page(driver) -> LoginPage:
    return LoginPage(driver)


@pytest.fixture()
def inventory_page(driver) -> InventoryPage:
    return InventoryPage(driver)


@pytest.fixture()
def cart_page(driver) -> CartPage:
    return CartPage(driver)


@pytest.fixture()
def checkout_page(driver) -> CheckoutPage:
    return CheckoutPage(driver)
