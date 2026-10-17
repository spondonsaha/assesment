"""Shared assertion helpers that produce readable failure messages."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Iterable

import allure
import pytest
from pytest import fail

RATE_LIMIT_STATUS = 429
RATE_LIMIT_HELP = (
    "ReqRes anonymous demo limit reached (429 - 40 requests/day per IP). "
    "Set the REQRES_API_KEY environment variable (free signup at https://app.reqres.in) "
    "for a higher limit, or retry after the daily reset. "
    "Set REQRES_ON_RATE_LIMIT=fail to treat this as a hard failure instead of a skip."
)


def _rate_limit_policy() -> str:
    return os.getenv("REQRES_ON_RATE_LIMIT", "skip").strip().lower()


def assert_equal(actual, expected, message: str = "") -> None:
    if actual != expected:
        fail(f"{message} | expected={expected!r} actual={actual!r}".strip(" |"))


def assert_contains(haystack: str, needle: str, message: str = "") -> None:
    if needle not in (haystack or ""):
        fail(f"{message} | expected to contain {needle!r} in {haystack!r}".strip(" |"))


def assert_all_in_order(actual: Iterable[str], expected: Iterable[str], message: str = "") -> None:
    actual_list, expected_list = list(actual), list(expected)
    if actual_list != expected_list:
        fail(f"{message} | expected={expected_list!r} actual={actual_list!r}".strip(" |"))


@allure.step("Assert HTTP status {expected}")
def assert_status_code(response, expected) -> None:
    """Mandatory response-code validation used by every API request.

    ``expected`` accepts an int, an iterable of ints, or a class string such as
    ``"4xx"`` / ``"2xx"``.
    """
    if isinstance(expected, str) and expected.lower().endswith("xx"):
        low = int(expected[0]) * 100
        ok = low <= response.status_code <= low + 99
    else:
        expected_codes = expected if isinstance(expected, (list, tuple, set)) else [expected]
        ok = response.status_code in expected_codes

    if response.status_code == RATE_LIMIT_STATUS and not ok:
        if _rate_limit_policy() == "fail":
            fail(RATE_LIMIT_HELP)
        pytest.skip(RATE_LIMIT_HELP)

    if not ok:
        fail(
            "Unexpected HTTP status | "
            f"expected={expected} actual={response.status_code} | "
            f"url={response.request.method} {response.url} | body={response.text[:500]}"
        )


def assert_is_4xx(response) -> None:
    """Q8 helper: assert the response is a client error (4xx)."""
    if not (400 <= response.status_code <= 499):
        fail(
            "Expected a 4xx client error | "
            f"actual={response.status_code} | "
            f"url={response.request.method} {response.url} | body={response.text[:500]}"
        )


def parse_iso_timestamp(value: str) -> datetime:
    """Parse a ReqRes ``updatedAt`` (e.g. 2026-10-17T11:48:11.034Z)."""
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        fail(f"updatedAt is not a valid ISO-8601 timestamp: {value!r}")
        raise


def assert_recent_timestamp(value: str, max_age_seconds: int = 120) -> datetime:
    """Assert a timestamp is within ``max_age_seconds`` of now (UTC)."""
    ts = parse_iso_timestamp(value)
    now = datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    age = (now - ts).total_seconds()
    if age < -30 or age > max_age_seconds:
        fail(
            f"updatedAt is not recent | value={value!r} | age_seconds={age:.1f} "
            f"(allowed 0..{max_age_seconds})"
        )
    return ts
