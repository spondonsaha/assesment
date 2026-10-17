"""UI Q1 [Mark 10] - locked_out_user shows the lock-out error message."""

import allure
import pytest

from config import settings

pytestmark = [pytest.mark.ui, pytest.mark.q1]


@allure.epic("SauceDemo UI")
@allure.feature("Authentication")
@allure.story("Q1 - Locked out user")
@allure.title("Q1 - Login with locked_out_user shows the lock-out error")
@allure.severity(allure.severity_level.CRITICAL)
def test_locked_out_user_error(login_page):
    login_page.load()

    with allure.step("Attempt login with locked_out_user"):
        login_page.login(settings.SAUCEDEMO_USERS["locked_out"])

    with allure.step("Verify the lock-out error message"):
        error = login_page.error_message()
        allure.attach(error, "error-message", allure.attachment_type.TEXT)
        assert error == settings.LOCKED_OUT_ERROR, (
            f"Unexpected error message | expected={settings.LOCKED_OUT_ERROR!r} actual={error!r}"
        )

    with allure.step("Verify the user stays on the login page"):
        assert login_page.is_loaded(), "Login page should still be displayed after a failed login"
