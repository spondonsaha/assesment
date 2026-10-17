"""API Q3 [Mark 10] - login with registered credentials and capture authToken."""

import allure
import pytest

from api.auth import login_and_store

pytestmark = [pytest.mark.api, pytest.mark.q3_api]


@allure.epic("ReqRes API")
@allure.feature("Authentication")
@allure.story("Q3 - Login")
@allure.title("Q3 - Login with registered credentials captures authToken")
@allure.severity(allure.severity_level.BLOCKER)
def test_login_captures_auth_token(api_client, store):
    with allure.step("POST /login with registered credentials (expect 200)"):
        token = login_and_store(api_client, store)

    with allure.step("Verify a non-empty authToken was captured and stored"):
        assert isinstance(token, str) and token.strip(), "authToken must be a non-empty string"
        assert store["authToken"] == token, "authToken was not persisted in the store"
        allure.attach(token, "authToken", allure.attachment_type.TEXT)
