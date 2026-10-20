
import os
import re
import time

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

URL = "https://www.saucedemo.com/"
PASSWORD = "secret_sauce"
WAIT = 60        
PAUSE = 0.8     


def new_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--window-size=1440,900")
    if os.getenv("SELENIUM_HEADLESS") == "1":
        options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    return driver


def wait_for(driver, timeout=WAIT):
    return WebDriverWait(driver, timeout)


def pause(seconds=PAUSE):
    time.sleep(seconds)


def retry(action, attempts=4):
    """SauceDemo is a React app; re-run an action if an element goes stale."""
    for _ in range(attempts - 1):
        try:
            return action()
        except StaleElementReferenceException:
            pass
    return action()


def click(driver, locator):
    def do():
        element = wait_for(driver).until(EC.element_to_be_clickable(locator))
        driver.execute_script("arguments[0].click();", element)

    retry(do)


def wait_invisible(driver, locator, timeout=WAIT):
    return wait_for(driver, timeout).until(EC.invisibility_of_element_located(locator))


def fill(driver, field_id, value):
    for _ in range(3):
        field = wait_for(driver).until(EC.element_to_be_clickable((By.ID, field_id)))
        field.click()
        field.clear()
        field.send_keys(value)
        if field.get_attribute("value") == value:
            return
    field = driver.find_element(By.ID, field_id)
    driver.execute_script(
        "const e = arguments[0], v = arguments[1];"
        "const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;"
        "setter.call(e, v);"
        "e.dispatchEvent(new Event('input', {bubbles: true}));"
        "e.dispatchEvent(new Event('change', {bubbles: true}));",
        field,
        value,
    )


def to_number(text):
    return float(re.search(r"[\d.]+", text).group())


def login(driver, username):
    driver.get(URL)
    wait_for(driver).until(EC.visibility_of_element_located((By.ID, "login-button")))
    driver.find_element(By.ID, "user-name").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(PASSWORD)
    click(driver, (By.ID, "login-button"))


def cart_count(driver):
    badges = driver.find_elements(By.CLASS_NAME, "shopping_cart_badge")
    return int(badges[0].text) if badges else 0


def menu_is_open(driver):
    def read_state():
        wrap = driver.find_element(By.CLASS_NAME, "bm-menu-wrap")
        return wrap.get_attribute("aria-hidden") == "false"

    return retry(read_state)


def open_menu(driver):
    if not menu_is_open(driver):
        click(driver, (By.ID, "react-burger-menu-btn"))
    wait_for(driver).until(EC.element_to_be_clickable((By.ID, "reset_sidebar_link")))


def close_menu(driver):
    if menu_is_open(driver):
        driver.execute_script("document.getElementById('react-burger-menu-btn').click();")
        wait_for(driver).until(lambda d: not menu_is_open(d))


def reset_app_state(driver):
    open_menu(driver)
    click(driver, (By.ID, "reset_sidebar_link"))
    wait_invisible(driver, (By.CLASS_NAME, "shopping_cart_badge"), timeout=10)
    close_menu(driver)


def logout(driver):
    open_menu(driver)
    click(driver, (By.ID, "logout_sidebar_link"))
    wait_for(driver).until(EC.visibility_of_element_located((By.ID, "login-button")))


def add_to_cart(driver, product_name):
    before = cart_count(driver)

    def click_add():
        for item in driver.find_elements(By.CLASS_NAME, "inventory_item"):
            title = item.find_element(By.CLASS_NAME, "inventory_item_name").text
            if title == product_name:
                button = item.find_element(By.TAG_NAME, "button")
                driver.execute_script("arguments[0].click();", button)
                return
        raise AssertionError(f"Product not found: {product_name}")

    retry(click_add)
    wait_for(driver).until(lambda d: cart_count(driver) == before + 1)


def start_checkout(driver, first_name="John", last_name="Doe", zip_code="12345"):
    click(driver, (By.CLASS_NAME, "shopping_cart_link"))
    wait_for(driver).until(EC.url_contains("cart.html"))
    click(driver, (By.ID, "checkout"))
    wait_for(driver).until(EC.url_contains("checkout-step-one.html"))
    wait_for(driver).until(EC.visibility_of_element_located((By.ID, "first-name")))
    for field_id, value in (("first-name", first_name), ("last-name", last_name), ("postal-code", zip_code)):
        fill(driver, field_id, value)
    click(driver, (By.ID, "continue"))
    wait_for(driver).until(EC.url_contains("checkout-step-two.html"))


def read_overview(driver):
    wait_for(driver).until(EC.visibility_of_element_located((By.CLASS_NAME, "summary_total_label")))
    names = [e.text for e in driver.find_elements(By.CSS_SELECTOR, ".cart_item .inventory_item_name")]
    prices = [to_number(e.text) for e in driver.find_elements(By.CSS_SELECTOR, ".cart_item .inventory_item_price")]
    subtotal = to_number(driver.find_element(By.CLASS_NAME, "summary_subtotal_label").text)
    tax = to_number(driver.find_element(By.CLASS_NAME, "summary_tax_label").text)
    total = to_number(driver.find_element(By.CLASS_NAME, "summary_total_label").text)
    assert abs(sum(prices) - subtotal) < 0.01, "subtotal does not match the item prices"
    return names, subtotal, tax, total


def finish_order(driver):
    click(driver, (By.ID, "finish"))
    wait_for(driver).until(EC.url_contains("checkout-complete.html"))
    header = wait_for(driver).until(
        EC.visibility_of_element_located((By.CLASS_NAME, "complete-header"))
    )
    return header.text


def back_home(driver):
    click(driver, (By.ID, "back-to-products"))
    wait_for(driver).until(EC.url_contains("inventory.html"))


def q1_locked_out_user(driver):
    print("  -> logging in as locked_out_user")
    login(driver, "locked_out_user")
    error = wait_for(driver).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "h3[data-test='error']"))
    ).text
    expected = "Epic sadface: Sorry, this user has been locked out."
    assert error == expected, f"unexpected message: {error}"
    print("  -> error shown:", error)
    pause(2)


def q2_standard_user(driver):
    products = ["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Bolt T-Shirt"]

    print("  -> logging in as standard_user")
    login(driver, "standard_user")
    wait_for(driver).until(EC.visibility_of_element_located((By.CLASS_NAME, "inventory_list")))

    print("  -> resetting app state")
    reset_app_state(driver)

    for product in products:
        print("  -> adding to cart:", product)
        add_to_cart(driver, product)
    assert cart_count(driver) == 3, "cart should hold 3 items"

    print("  -> going through checkout")
    start_checkout(driver)
    names, subtotal, tax, total = read_overview(driver)
    print("  -> products on overview:", names)
    print("  -> total price:", total)
    assert sorted(names) == sorted(products), f"wrong products: {names}"
    assert abs(subtotal + tax - total) < 0.01, "total does not match subtotal + tax"

    header = finish_order(driver)
    print("  -> confirmation:", header)
    assert header == "Thank you for your order!", f"unexpected confirmation: {header}"

    print("  -> resetting app state and logging out")
    back_home(driver)
    reset_app_state(driver)
    logout(driver)
    pause(1)


def q3_performance_glitch_user(driver):
    print("  -> logging in as performance_glitch_user (this one is slow)")
    login(driver, "performance_glitch_user")
    wait_for(driver).until(EC.visibility_of_element_located((By.CLASS_NAME, "inventory_list")))

    print("  -> resetting app state")
    reset_app_state(driver)

    print("  -> sorting products by Name (Z to A)")
    Select(driver.find_element(By.CLASS_NAME, "product_sort_container")).select_by_value("za")
    first_product = wait_for(driver).until(
        lambda d: d.find_elements(By.CLASS_NAME, "inventory_item_name")[0].text
    )
    print("  -> first product after sorting:", first_product)

    add_to_cart(driver, first_product)

    print("  -> going through checkout")
    start_checkout(driver)
    names, subtotal, tax, total = read_overview(driver)
    print("  -> products on overview:", names)
    print("  -> total price:", total)
    assert names == [first_product], f"wrong products: {names}"
    assert abs(subtotal + tax - total) < 0.01, "total does not match subtotal + tax"

    header = finish_order(driver)
    print("  -> confirmation:", header)
    assert header == "Thank you for your order!", f"unexpected confirmation: {header}"

    print("  -> resetting app state and logging out")
    back_home(driver)
    reset_app_state(driver)
    logout(driver)
    pause(1)


def main():
    print("Starting SauceDemo UI tests. A Chrome window will open...\n")
    driver = new_driver()
    scenarios = [
        ("Q1 - locked_out_user shows error", q1_locked_out_user),
        ("Q2 - standard_user full purchase", q2_standard_user),
        ("Q3 - performance_glitch_user sorted purchase", q3_performance_glitch_user),
    ]

    results = []
    try:
        for name, run in scenarios:
            print(f"=== {name} ===")
            try:
                run(driver)
                results.append((name, "PASS"))
            except Exception as error:
                results.append((name, f"FAIL: {error}"))
            print()
    finally:
        print("===== SUMMARY =====")
        for name, result in results:
            print(f"  {result:<5}  {name}")
        try:
            input("\nPress Enter to close the browser...")
        except EOFError:
            pass
        driver.quit()


if __name__ == "__main__":
    main()
