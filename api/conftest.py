"""API suite fixtures: shared client and cross-test data store."""

from __future__ import annotations

import allure
import pytest

from api.api_client import ApiClient
from api.auth import login_and_store


@pytest.fixture()
def api_client() -> ApiClient:
    return ApiClient()


@pytest.fixture(scope="session")
def store() -> dict:
    """Session-scoped store shared across API tests (authToken, userId, ...)."""
    return {
        "userId": None,
        "authToken": None,
        "user": None,
        "updated_profile": None,
        "patched_profile": None,
    }


@pytest.fixture()
def auth_token(api_client, store) -> str:
    """Return a valid token, logging in once if the suite did not run Q3 first."""
    if not store.get("authToken"):
        with allure.step("Auth token absent - performing a seed login"):
            login_and_store(api_client, store)
    return store["authToken"]
