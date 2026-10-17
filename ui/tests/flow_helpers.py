"""Reusable checkout-overview verification shared by UI scenarios Q2 and Q3."""

from __future__ import annotations

import allure


def assert_overview_and_collect(checkout_page, expected_products):
    """Verify product names and price arithmetic on the checkout overview.

    Checks:
      * the displayed product names match the expected products,
      * subtotal equals the sum of the item prices,
      * total equals subtotal + tax.

    Returns the displayed total price.
    """
    displayed = checkout_page.product_names()
    prices = checkout_page.item_prices()
    subtotal = checkout_page.subtotal()
    tax = checkout_page.tax()
    total = checkout_page.total()

    with allure.step("Verify product names on the checkout overview"):
        assert sorted(displayed) == sorted(expected_products), (
            f"Product mismatch | expected={sorted(expected_products)} actual={sorted(displayed)}"
        )

    with allure.step("Verify subtotal, tax and total arithmetic"):
        assert abs(sum(prices) - subtotal) < 0.01, (
            f"Subtotal mismatch | sum(item prices)={sum(prices):.2f} displayed={subtotal:.2f}"
        )
        assert abs((subtotal + tax) - total) < 0.01, (
            f"Total mismatch | subtotal+tax={subtotal + tax:.2f} displayed={total:.2f}"
        )

    allure.attach(
        f"products={displayed}\nprices={prices}\nsubtotal={subtotal}\ntax={tax}\ntotal={total}",
        name="checkout-overview",
        attachment_type=allure.attachment_type.TEXT,
    )
    return total
