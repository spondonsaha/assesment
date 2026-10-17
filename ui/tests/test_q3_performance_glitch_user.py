"""UI Q3 [Mark 10] - performance_glitch_user sorted purchase journey.

Reset app state -> filter Name (Z to A) -> add the first product -> checkout ->
verify names & total -> finish -> verify success message -> reset -> log out.

performance_glitch_user is intentionally slow, so every page object is created
with a larger explicit-wait timeout.
"""

import allure
import pytest

from config import settings
from ui.pages.cart_page import CartPage
from ui.pages.checkout_page import CheckoutPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.login_page import LoginPage
from ui.tests.flow_helpers import assert_overview_and_collect

pytestmark = [pytest.mark.ui, pytest.mark.q3]


@allure.epic("SauceDemo UI")
@allure.feature("Purchase journey")
@allure.story("Q3 - Performance glitch user")
@allure.title("Q3 - performance_glitch_user: sort Z-A, buy first item, finish, reset, logout")
@allure.severity(allure.severity_level.CRITICAL)
def test_performance_glitch_user_sorted_journey(driver):
    timeout = settings.UI_GLITCH_TIMEOUT
    login_page = LoginPage(driver, timeout=timeout)
    inventory_page = InventoryPage(driver, timeout=timeout)
    cart_page = CartPage(driver, timeout=timeout)
    checkout_page = CheckoutPage(driver, timeout=timeout)

    with allure.step("Log in as performance_glitch_user"):
        login_page.load()
        login_page.login(settings.SAUCEDEMO_USERS["performance_glitch"])
        inventory_page.wait_loaded()

    with allure.step("Reset the App State from the hamburger menu"):
        inventory_page.reset_app_state()

    with allure.step("Filter products by Name (Z to A)"):
        inventory_page.sort_by("za")
        names = inventory_page.product_names()
        assert names == sorted(names, reverse=True), f"Products are not sorted Z to A: {names}"

    with allure.step("Add the first product to the cart"):
        first_product = inventory_page.first_product_name()
        allure.attach(first_product, "first-product (Z->A)", allure.attachment_type.TEXT)
        inventory_page.add_first_to_cart()
        assert inventory_page.cart_count() == 1, "Cart badge should be 1"

    with allure.step("Open the cart and start checkout"):
        inventory_page.go_to_cart()
        assert cart_page.product_names() == [first_product], (
            f"Cart contents mismatch | actual={cart_page.product_names()}"
        )
        cart_page.checkout()

    with allure.step("Enter checkout information and continue"):
        checkout_page.fill_information().continue_to_overview()

    with allure.step("Verify product names and total price on the overview"):
        total = assert_overview_and_collect(checkout_page, [first_product])

    with allure.step("Finish the purchase"):
        checkout_page.finish()

    with allure.step("Verify the successful order message"):
        header = checkout_page.complete_header()
        assert header == settings.ORDER_COMPLETE_HEADER, (
            f"Order confirmation mismatch | expected={settings.ORDER_COMPLETE_HEADER!r} actual={header!r}"
        )
        allure.attach(
            f"order_total={total}\nconfirmation={header}",
            "order-confirmation",
            allure.attachment_type.TEXT,
        )

    with allure.step("Return to inventory, reset App State and log out"):
        checkout_page.back_home()
        inventory_page.reset_app_state()
        inventory_page.logout()
        assert login_page.is_loaded(), "Did not return to the login page after logout"
