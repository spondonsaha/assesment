"""API Q4 [Mark 10] - GET user by userId and verify name & email."""

import allure
import pytest

from config import settings

pytestmark = [pytest.mark.api, pytest.mark.q4]


@allure.epic("ReqRes API")
@allure.feature("Users")
@allure.story("Q4 - Get user")
@allure.title("Q4 - GET user by id returns the expected name and email")
@allure.severity(allure.severity_level.CRITICAL)
def test_get_user_by_id(api_client, store, auth_token):
    user_id = store.get("userId") or settings.API_USER_ID
    expected = settings.API_USER_EXPECTED

    with allure.step(f"GET /users/{user_id} (expect 200)"):
        response = api_client.get(f"/users/{user_id}", expected=200)

    with allure.step("Verify id, name and email match the expected user"):
        data = response.json().get("data", {})
        assert data.get("id") == user_id, f"id mismatch | actual={data.get('id')}"

        full_name = f"{data.get('first_name', '')} {data.get('last_name', '')}".strip()
        expected_name = f"{expected['first_name']} {expected['last_name']}"
        assert full_name == expected_name, (
            f"name mismatch | expected={expected_name!r} actual={full_name!r}"
        )
        assert data.get("email") == expected["email"], (
            f"email mismatch | expected={expected['email']!r} actual={data.get('email')!r}"
        )

    with allure.step("Persist the retrieved user for later requests"):
        store["userId"] = user_id
        store["user"] = data
        allure.attach(
            f"userId={user_id}\nname={full_name}\nemail={data.get('email')}",
            "retrieved-user",
            allure.attachment_type.TEXT,
        )
