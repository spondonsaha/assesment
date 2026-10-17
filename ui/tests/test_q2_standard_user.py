"""UI Q2 [Mark 20] - standard_user full purchase journey.

Reset app state -> add three items -> checkout -> verify names & total ->
finish -> verify success message -> reset app state -> log out.
"""

import allure
import pytest

from config import settings
from ui.tests.flow_helpers import assert_overview_and_collect

pytestmark = [pytest.mark.ui, pytest.mark.q2]


@allure.epic("SauceDemo UI")
@allure.feature("Purchase journey")
@allure.story("Q2 - Standard user checkout")
@allure.title("Q2 - Standard user: reset, add 3 items, checkout, finish, reset, logout")
@allure.severity(allure.severity_level.BLOCKER)
def test_standard_user_checkout_journey(login_page, inventory_page, cart_page, checkout_page, driver):
    with allure.step("Log in as standard_user"):
        login_page.load()
        login_page.login(settings.SAUCEDEMO_USERS["standard"])
        inventory_page.wait_loaded()

    with allure.step("Reset the App State from the hamburger menu"):
        inventory_page.reset_app_state()

    with allure.step("Add three products to the cart"):
        for product in settings.STANDARD_USER_PRODUCTS:
            inventory_page.add_to_cart(product)
        assert inventory_page.cart_count() == len(settings.STANDARD_USER_PRODUCTS), (
            f"Cart badge mismatch | expected={len(settings.STANDARD_USER_PRODUCTS)} "
            f"actual={inventory_page.cart_count()}"
        )

    with allure.step("Open the cart and start checkout"):
        inventory_page.go_to_cart()
        cart_page.wait_loaded()
        assert sorted(cart_page.product_names()) == sorted(settings.STANDARD_USER_PRODUCTS), (
            f"Cart contents mismatch | actual={cart_page.product_names()}"
        )
        cart_page.checkout()

    with allure.step("Enter checkout information and continue"):
        checkout_page.fill_information().continue_to_overview()

    with allure.step("Verify product names and total price on the overview"):
        total = assert_overview_and_collect(checkout_page, settings.STANDARD_USER_PRODUCTS)

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
