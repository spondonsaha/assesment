"""API Q6 [Mark 10] - PATCH a single field and verify only that field changed."""

import allure
import pytest

from config import settings
from utils.assertions import assert_recent_timestamp

pytestmark = [pytest.mark.api, pytest.mark.q6]

# Fields that must NOT be echoed when patching only the job field.
UNTOUCHED_FIELDS = ["name", "email", "first_name", "last_name"]


@allure.epic("ReqRes API")
@allure.feature("Users")
@allure.story("Q6 - Patch single field")
@allure.title("Q6 - PATCH changes only the targeted field and refreshes updatedAt")
@allure.severity(allure.severity_level.CRITICAL)
def test_patch_single_field(api_client, store, auth_token):
    user_id = store.get("userId") or settings.API_USER_ID
    payload = {"job": settings.API_PATCHED_JOB}

    with allure.step(f"PATCH /users/{user_id} changing only 'job' (expect 200)"):
        response = api_client.patch(f"/users/{user_id}", expected=200, json=payload)

    body = response.json()

    with allure.step("Verify the patched field holds the new value"):
        assert body.get("job") == payload["job"], (
            f"job mismatch | expected={payload['job']!r} actual={body.get('job')!r}"
        )

    with allure.step("Verify no other user fields were modified by the PATCH"):
        leaked = [field for field in UNTOUCHED_FIELDS if field in body]
        assert not leaked, f"PATCH modified/echoed unexpected fields: {leaked}"

    with allure.step("Verify updatedAt is present and recent"):
        updated_at = body.get("updatedAt")
        assert updated_at, "updatedAt missing from the PATCH response"
        assert_recent_timestamp(updated_at)

    with allure.step("Persist the patched profile"):
        store["patched_profile"] = body
        allure.attach(
            f"patched={payload}\nresponse={body}",
            "patched-profile",
            allure.attachment_type.TEXT,
        )
