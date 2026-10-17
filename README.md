# Automation Testing Assessment

Simple automation: a Selenium script that opens a visible Chrome window and runs the SauceDemo scenarios, and a Postman collection to run the ReqRes API checks.

## Setup

For UI tests only:
```powershell
pip install selenium
```

Chrome is required for the UI script (Selenium Manager downloads the driver on its own).

## UI tests (SauceDemo)

**Visible Chrome window (default):**
```powershell
python saucedemo_ui.py
```

**Headless (no window):**
```powershell
$env:SELENIUM_HEADLESS="1"; python saucedemo_ui.py
```

Runs:
* **Q1** – `locked_out_user` shows the lock-out error
* **Q2** – `standard_user`: reset app state → add 3 items → checkout → verify products & total → finish → success message → reset → logout
* **Q3** – `performance_glitch_user`: reset → sort Name (Z to A) → add first product → checkout → verify names & total → finish → success message → reset → logout

At the end it prints a PASS/FAIL summary. Press Enter to close the browser.

## API tests (ReqRes – Postman)

The API automation is the Postman collection in `postman/` with built-in tests (status codes, assertions, and chained values).

**Run in Postman:** Import `postman/ReqRes_API.postman_collection.json` and `postman/ReqRes.postman_environment.json`, then run the collection.

**Run via Newman (CLI):**

```powershell
newman run postman/ReqRes_API.postman_collection.json -e postman/ReqRes.postman_environment.json
```

> ReqRes allows 40 requests/day for anonymous use. If you hit the limit, wait and run again.

## Notes
- No manual WebDriver download needed (Selenium Manager handles it).
- All requests validate HTTP status codes. The collection covers login/authToken (Q3), get user + name/email (Q4), PUT with `updatedAt` (Q5), PATCH single field (Q6), and bad requests returning 4xx (Q8).
