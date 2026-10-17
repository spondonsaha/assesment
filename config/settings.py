"""Central configuration for UI and API automation suites."""

import os

# ---------------------------------------------------------------------------
# UI - SauceDemo
# ---------------------------------------------------------------------------
UI_BASE_URL = "https://www.saucedemo.com/"

SAUCEDEMO_USERS = {
    "standard": "standard_user",
    "locked_out": "locked_out_user",
    "problem": "problem_user",
    "performance_glitch": "performance_glitch_user",
    "error": "error_user",
    "visual": "visual_user",
}
SAUCEDEMO_PASSWORD = "secret_sauce"

LOCKED_OUT_ERROR = (
    "Epic sadface: Sorry, this user has been locked out."
)
ORDER_COMPLETE_HEADER = "Thank you for your order!"

# Products used by the standard_user journey (Q2). Order is the on-page order.
STANDARD_USER_PRODUCTS = [
    "Sauce Labs Backpack",
    "Sauce Labs Bike Light",
    "Sauce Labs Bolt T-Shirt",
]

# ---------------------------------------------------------------------------
# API - ReqRes
# ---------------------------------------------------------------------------
API_BASE_URL = "https://reqres.in/api"

# ReqRes WAF blocks the default ``Python-urllib`` user-agent; a real one is
# required for every request. ``requests`` already works, but we set it
# explicitly so the behaviour is deterministic everywhere.
API_HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AutomationAssessment/1.0",
}

# Optional: the ReqRes anonymous demo is limited to 40 requests/day per IP.
# A free API key (https://app.reqres.in) raises the limit. When REQRES_API_KEY
# is set, it is sent as the x-api-key header on every request.
REQRES_API_KEY = os.getenv("REQRES_API_KEY", "").strip()
if REQRES_API_KEY:
    API_HEADERS["x-api-key"] = REQRES_API_KEY

# Registered credentials for POST /login.
API_LOGIN_EMAIL = "eve.holt@reqres.in"
API_LOGIN_PASSWORD = "cityslicka"

# The user we read/update. ReqRes seed data for id=2.
API_USER_ID = 2
API_USER_EXPECTED = {
    "id": 2,
    "email": "janet.weaver@reqres.in",
    "first_name": "Janet",
    "last_name": "Weaver",
}

# PUT /users/{id} payload.
API_UPDATED_NAME = "Janet Weaver"
API_UPDATED_JOB = "Senior QA Automation Engineer"

# PATCH /users/{id} - only this single field must change.
API_PATCHED_JOB = "Lead QA Automation Engineer"

# Generic request timeout (seconds).
API_TIMEOUT = 30

# UI explicit-wait default (seconds). performance_glitch_user is intentionally
# slow, so callers may pass a larger value.
UI_TIMEOUT = int(os.getenv("UI_TIMEOUT", "20"))
UI_GLITCH_TIMEOUT = int(os.getenv("UI_GLITCH_TIMEOUT", "60"))
