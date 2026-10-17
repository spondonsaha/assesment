"""Root pytest configuration shared by the UI and API suites."""

import os

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="Run the Selenium browser in headed (visible) mode. Default is headless.",
    )
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "edge"],
        help="Browser to use for UI tests (default: chrome).",
    )


@pytest.fixture(scope="session")
def headed(request) -> bool:
    return request.config.getoption("--headed")


@pytest.fixture(scope="session")
def browser_name(request) -> str:
    return request.config.getoption("--browser")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach a screenshot to Allure when a UI test fails."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed:
        return
    driver = item.funcargs.get("driver")
    if driver is None:
        return
    try:
        import allure

        allure.attach(
            driver.get_screenshot_as_png(),
            name=f"failure-{item.name}",
            attachment_type=allure.attachment_type.PNG,
        )
    except Exception:
        pass
