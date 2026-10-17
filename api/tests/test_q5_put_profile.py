"""API Q5 [Mark 10] - PUT updated profile and verify updatedAt timestamp."""

import allure
import pytest

from config import settings
from utils.assertions import assert_recent_timestamp

pytestmark = [pytest.mark.api, pytest.mark.q5]


@allure.epic("ReqRes API")
@allure.feature("Users")
@allure.story("Q5 - Update profile")
@allure.title("Q5 - PUT updated profile returns echoed fields and a recent updatedAt")
@allure.severity(allure.severity_level.CRITICAL)
def test_put_updated_profile(api_client, store, auth_token):
    user_id = store.get("userId") or settings.API_USER_ID
    payload = {"name": settings.API_UPDATED_NAME, "job": settings.API_UPDATED_JOB}

    with allure.step(f"PUT /users/{user_id} with the updated profile (expect 200)"):
        response = api_client.put(f"/users/{user_id}", expected=200, json=payload)

    body = response.json()

    with allure.step("Verify the updated name and job are echoed back"):
        assert body.get("name") == payload["name"], (
            f"name mismatch | expected={payload['name']!r} actual={body.get('name')!r}"
        )
        assert body.get("job") == payload["job"], (
            f"job mismatch | expected={payload['job']!r} actual={body.get('job')!r}"
        )

    with allure.step("Verify updatedAt is present and is a recent ISO-8601 timestamp"):
        updated_at = body.get("updatedAt")
        assert updated_at, "updatedAt missing from the PUT response"
        assert_recent_timestamp(updated_at)

    with allure.step("Persist the updated profile"):
        store["updated_profile"] = body
        allure.attach(updated_at, "updatedAt", allure.attachment_type.TEXT)
