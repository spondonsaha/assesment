"""API Q8 [Mark 20] - execute bad requests using stored data and assert 4xx.

Each request reuses data captured earlier in the suite (the registered email
and the userId) and asserts the API responds with a client error (4xx).
"""

import allure
import pytest

from config import settings
from utils.assertions import assert_is_4xx

pytestmark = [pytest.mark.api, pytest.mark.q8]


@allure.epic("ReqRes API")
@allure.feature("Negative testing")
@allure.story("Q8 - Bad requests")
@allure.title("Bad requests return 4xx client errors")
@allure.severity(allure.severity_level.CRITICAL)
class TestBadRequests:
    def _registered_email(self, store) -> str:
        return store.get("login_email") or settings.API_LOGIN_EMAIL

    def _unknown_user_id(self, store) -> int:
        return (store.get("userId") or settings.API_USER_ID) + 999_999

    @allure.title("Q8.1 - POST /login with stored email but no password -> 4xx")
    def test_login_missing_password(self, api_client, store, auth_token):
        email = self._registered_email(store)
        response = api_client.post("/login", expected=400, json={"email": email})
        assert_is_4xx(response)
        assert response.status_code == 400, response.text
        assert response.json().get("error") == "Missing password", response.text

    @allure.title("Q8.2 - POST /login with an unregistered email -> 4xx")
    def test_login_unknown_user(self, api_client, store, auth_token):
        response = api_client.post(
            "/login",
            expected=400,
            json={"email": "not.a.user@reqres.invalid", "password": settings.API_LOGIN_PASSWORD},
        )
        assert_is_4xx(response)
        assert response.status_code == 400, response.text
        assert response.json().get("error") == "user not found", response.text

    @allure.title("Q8.3 - GET a non-existent user derived from the stored userId -> 4xx")
    def test_get_unknown_user(self, api_client, store, auth_token):
        unknown_id = self._unknown_user_id(store)
        response = api_client.get(f"/users/{unknown_id}", expected=404)
        assert_is_4xx(response)
        assert response.status_code == 404, response.text

    @allure.title("Q8.4 - POST /register with stored email but no password -> 4xx")
    def test_register_missing_password(self, api_client, store, auth_token):
        email = self._registered_email(store)
        response = api_client.post("/register", expected=400, json={"email": email})
        assert_is_4xx(response)
        assert response.status_code == 400, response.text
        assert response.json().get("error") == "Missing password", response.text
