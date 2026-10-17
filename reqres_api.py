"""ReqRes API automation.

Run it with:

    python reqres_api.py
"""

import requests

BASE = "https://reqres.in/api"
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0",
}
EMAIL = "eve.holt@reqres.in"
PASSWORD = "cityslicka"
USER_ID = 2

auth_token = None


def check(response, expected):
    """Every request's status code is validated here."""
    if response.status_code == 429:
        raise RuntimeError(
            "ReqRes daily limit reached (40 requests/day for anonymous use). "
            "Please try again later."
        )
    assert response.status_code == expected, (
        f"expected {expected}, got {response.status_code}: {response.text}"
    )
    return response


def q3_login():
    global auth_token
    print("  -> POST /login")
    response = check(
        requests.post(f"{BASE}/login", json={"email": EMAIL, "password": PASSWORD}, headers=HEADERS),
        200,
    )
    auth_token = response.json().get("token")
    assert auth_token, "no authToken returned"
    print("  -> captured authToken:", auth_token)


def q4_get_user():
    print(f"  -> GET /users/{USER_ID}")
    response = check(requests.get(f"{BASE}/users/{USER_ID}", headers=HEADERS), 200)
    user = response.json()["data"]
    name = f"{user['first_name']} {user['last_name']}"
    assert name == "Janet Weaver", f"unexpected name: {name}"
    assert user["email"] == "janet.weaver@reqres.in", f"unexpected email: {user['email']}"
    print("  -> user:", name, "-", user["email"])


def q5_update_profile():
    print(f"  -> PUT /users/{USER_ID}")
    payload = {"name": "Janet Weaver", "job": "Senior QA Automation Engineer"}
    response = check(requests.put(f"{BASE}/users/{USER_ID}", json=payload, headers=HEADERS), 200)
    body = response.json()
    assert body["name"] == payload["name"] and body["job"] == payload["job"], body
    assert body.get("updatedAt"), "no updatedAt returned"
    print("  -> updatedAt:", body["updatedAt"])


def q6_patch_field():
    print(f"  -> PATCH /users/{USER_ID}")
    response = check(
        requests.patch(f"{BASE}/users/{USER_ID}", json={"job": "Lead QA Automation Engineer"}, headers=HEADERS),
        200,
    )
    body = response.json()
    assert body["job"] == "Lead QA Automation Engineer", body
    assert "name" not in body, "PATCH changed more than the job field"
    print("  -> patched job:", body["job"])


def q8_bad_requests():
    print("  -> POST /login without password")
    response = check(requests.post(f"{BASE}/login", json={"email": EMAIL}, headers=HEADERS), 400)
    assert response.json()["error"] == "Missing password", response.text

    print("  -> POST /login with an unknown user")
    response = check(
        requests.post(f"{BASE}/login", json={"email": "nobody@nope.invalid", "password": "x"}, headers=HEADERS),
        400,
    )
    assert response.json()["error"] == "user not found", response.text

    print("  -> GET /users/999999 (does not exist)")
    check(requests.get(f"{BASE}/users/999999", headers=HEADERS), 404)

    print("  -> POST /register without password")
    response = check(requests.post(f"{BASE}/register", json={"email": EMAIL}, headers=HEADERS), 400)
    assert response.json()["error"] == "Missing password", response.text

    print("  -> all bad requests correctly returned 4xx")


def main():
    print("Starting ReqRes API tests...\n")
    tests = [
        ("Q3 - login and capture authToken", q3_login),
        ("Q4 - get user and verify name/email", q4_get_user),
        ("Q5 - update profile and verify updatedAt", q5_update_profile),
        ("Q6 - patch a single field", q6_patch_field),
        ("Q8 - bad requests return 4xx", q8_bad_requests),
    ]

    results = []
    for name, run in tests:
        print(f"=== {name} ===")
        try:
            run()
            results.append((name, "PASS"))
        except Exception as error:
            results.append((name, f"FAIL: {error}"))
        print()

    print("===== SUMMARY =====")
    for name, result in results:
        print(f"  {result:<5}  {name}")


if __name__ == "__main__":
    main()
