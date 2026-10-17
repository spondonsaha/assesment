"""Authentication helpers that persist the captured authToken."""

from __future__ import annotations

import allure

from config import settings
from utils.assertions import assert_equal


@allure.step("POST /login and capture authToken")
def login_and_store(api_client, store: dict, email: str = None, password: str = None) -> str:
    email = email or settings.API_LOGIN_EMAIL
    password = password if password is not None else settings.API_LOGIN_PASSWORD

    response = api_client.post(
        "/login",
        expected=200,
        json={"email": email, "password": password},
    )
    body = response.json()
    token = body.get("token")
    assert token, f"authToken missing from login response: {body}"
    assert_equal(response.status_code, 200, "Login should return 200")

    store["authToken"] = token
    store["login_email"] = email
    return token
